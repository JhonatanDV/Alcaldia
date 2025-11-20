"""
Dashboard views for maintenance system analytics and statistics.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncDate
from datetime import datetime, timedelta
from api.models import Maintenance, Equipment, Report
from api.permissions import IsAdminOrTechnician


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Get dashboard statistics for maintenance system.
    
    Returns:
        - Total counts (maintenances, equipment, reports)
        - Maintenances by type
        - Maintenances by dependency
        - Maintenances by month (last 12 months)
        - Recent maintenances
        - Top equipment by maintenance count
    """
    
    # Date range for stats (last 12 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Total counts
    total_maintenances = Maintenance.objects.count()
    total_equipment = Equipment.objects.count()
    total_reports = Report.objects.count()
    
    # Maintenances by type
    by_type = list(
        Maintenance.objects.values('maintenance_type')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    # Maintenances by dependency
    by_dependency = list(
        Maintenance.objects.exclude(dependencia__isnull=True)
        .exclude(dependencia='')
        .values('dependencia')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )
    
    # Maintenances by sede
    by_sede = list(
        Maintenance.objects.exclude(sede__isnull=True)
        .exclude(sede='')
        .values('sede')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )
    
    # Maintenances by month (last 12 months)
    by_month = list(
        Maintenance.objects.filter(maintenance_date__gte=start_date)
        .annotate(month=TruncMonth('maintenance_date'))
        .values('month')
        .annotate(
            total=Count('id'),
            computer=Count('id', filter=Q(maintenance_type='computer')),
            printer_scanner=Count('id', filter=Q(maintenance_type='printer_scanner'))
        )
        .order_by('month')
    )
    
    # Recent maintenances (last 10)
    recent_maintenances = []
    for m in Maintenance.objects.select_related('equipment').order_by('-maintenance_date', '-created_at')[:10]:
        recent_maintenances.append({
            'id': m.id,
            'equipment_code': m.equipment.code,
            'equipment_name': m.equipment.name,
            'maintenance_type': m.maintenance_type,
            'maintenance_date': m.maintenance_date,
            'performed_by': m.performed_by,
            'dependencia': m.dependencia,
            'sede': m.sede,
        })
    
    # Top equipment by maintenance count
    top_equipment = list(
        Equipment.objects.annotate(maintenance_count=Count('maintenances'))
        .order_by('-maintenance_count')[:10]
        .values('code', 'name', 'location', 'maintenance_count')
    )
    
    # Incidents vs normal maintenances
    incidents_count = Maintenance.objects.filter(is_incident=True).count()
    normal_count = Maintenance.objects.filter(is_incident=False).count()
    
    # Service ratings distribution
    ratings = list(
        Maintenance.objects.exclude(calificacion_servicio__isnull=True)
        .values('calificacion_servicio')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    return Response({
        'summary': {
            'total_maintenances': total_maintenances,
            'total_equipment': total_equipment,
            'total_reports': total_reports,
            'incidents_count': incidents_count,
            'normal_count': normal_count,
        },
        'by_type': by_type,
        'by_dependency': by_dependency,
        'by_sede': by_sede,
        'by_month': by_month,
        'recent_maintenances': recent_maintenances,
        'top_equipment': top_equipment,
        'ratings': ratings,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_equipment_stats(request):
    """
    Get equipment-specific statistics.
    """
    
    # Equipment with most recent maintenance
    equipment_with_last_maintenance = []
    for eq in Equipment.objects.all()[:20]:
        last_maintenance = eq.maintenances.order_by('-maintenance_date').first()
        equipment_with_last_maintenance.append({
            'id': eq.id,
            'code': eq.code,
            'name': eq.name,
            'location': eq.location,
            'last_maintenance_date': last_maintenance.maintenance_date if last_maintenance else None,
            'days_since_maintenance': (datetime.now().date() - last_maintenance.maintenance_date).days if last_maintenance else None,
            'total_maintenances': eq.maintenances.count(),
        })
    
    # Equipment without maintenance
    equipment_without_maintenance = list(
        Equipment.objects.annotate(maintenance_count=Count('maintenances'))
        .filter(maintenance_count=0)
        .values('id', 'code', 'name', 'location')
    )
    
    return Response({
        'equipment_with_last_maintenance': equipment_with_last_maintenance,
        'equipment_without_maintenance': equipment_without_maintenance,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_maintenance_timeline(request):
    """
    Get maintenance timeline data for calendar/timeline views.
    """
    
    # Get date range from query params or default to current month
    year = request.query_params.get('year', datetime.now().year)
    month = request.query_params.get('month', datetime.now().month)
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = datetime.now().year
        month = datetime.now().month
    
    # Get maintenances for the specified month
    maintenances_by_date = list(
        Maintenance.objects.filter(
            maintenance_date__year=year,
            maintenance_date__month=month
        )
        .annotate(date=TruncDate('maintenance_date'))
        .values('date')
        .annotate(
            total=Count('id'),
            computer=Count('id', filter=Q(maintenance_type='computer')),
            printer_scanner=Count('id', filter=Q(maintenance_type='printer_scanner')),
            incidents=Count('id', filter=Q(is_incident=True))
        )
        .order_by('date')
    )
    
    return Response({
        'year': year,
        'month': month,
        'maintenances_by_date': maintenances_by_date,
    })
