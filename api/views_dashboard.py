"""
Dashboard views with complete statistics and metrics.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from api.models import Maintenance, Equipment, Incident


class DashboardStatsView(APIView):
    """
    Estadísticas generales del dashboard
    """
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retorna estadísticas generales del sistema
        """
        # Estadísticas generales
        total_maintenances = Maintenance.objects.count()
        total_equipment = Equipment.objects.count()
        total_reports = Maintenance.objects.filter(reports__isnull=False).distinct().count()
        total_incidents = Incident.objects.count()
        
        # Mantenimientos por estado
        maintenances_by_status = Maintenance.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Mantenimientos por tipo
        maintenance_by_type = Maintenance.objects.values('maintenance_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Equipos más mantenidos
        equipment_most_maintenances = Equipment.objects.annotate(
            maintenance_count=Count('maintenances')
        ).order_by('-maintenance_count')[:5]
        
        equipment_data = [{
            'equipment_name': eq.name,
            'equipment_serial': eq.serial_number,  # ← Cambio aquí
            'maintenance_count': eq.maintenance_count
        } for eq in equipment_most_maintenances]
        
        # Calificaciones promedio
        avg_rating = 0
        
        return Response({
            'overview': {
                'total_maintenances': total_maintenances,
                'total_equipment': total_equipment,
                'total_reports': total_reports,
                'total_incidents': total_incidents,
            },
            'maintenances_by_status': list(maintenances_by_status),
            'maintenance_by_type': list(maintenance_by_type),
            'equipment_most_maintenances': equipment_data,
            'average_rating': avg_rating
        })


class DashboardChartsView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Datos para gráficos del dashboard
        """
        # Mantenimientos por mes (últimos 12 meses)
        today = timezone.now()
        maintenances_per_month = []
        
        for i in range(11, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            
            count = Maintenance.objects.filter(
                scheduled_date__gte=month_start,
                scheduled_date__lt=month_end
            ).count()
            
            maintenances_per_month.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })
        
        # Equipos con más mantenimientos
        equipment_most_maintenances = Equipment.objects.annotate(
            maintenance_count=Count('maintenances')
        ).order_by('-maintenance_count')[:10]
        
        equipment_data = [{
            'equipment_name': eq.name,
            'equipment_serial': eq.serial_number,  # ← Cambio aquí
            'maintenance_count': eq.maintenance_count
        } for eq in equipment_most_maintenances]
        
        # Mantenimientos por tipo
        maintenance_by_type = Maintenance.objects.values('maintenance_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'maintenances_per_month': maintenances_per_month,
            'equipment_most_maintenances': equipment_data,
            'maintenance_by_type': list(maintenance_by_type)
        })


class DashboardRecentActivityView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Actividad reciente del dashboard
        """
        # Mantenimientos recientes
        recent_maintenances = Maintenance.objects.select_related(
            'equipment', 'technician'
        ).order_by('-scheduled_date')[:10]
        
        recent_data = [{
            'id': m.id,
            'equipment_name': m.equipment.name,
            'equipment_serial': m.equipment.serial_number,  # ← Cambio aquí
            'maintenance_type': m.maintenance_type,
            'scheduled_date': m.scheduled_date,
            'completion_date': m.completion_date,
            'status': m.status,
            'technician_name': f"{m.technician.first_name} {m.technician.last_name}" if m.technician else 'Sin asignar'
        } for m in recent_maintenances]
        
        # Equipos que necesitan mantenimiento
        thirty_days_ago = timezone.now() - timedelta(days=30)
        equipment_needing_maintenance = Equipment.objects.filter(
            Q(maintenances__isnull=True) |
            Q(maintenances__completion_date__lt=thirty_days_ago)
        ).distinct()[:10]
        
        equipment_data = [{
            'id': eq.id,
            'name': eq.name,
            'serial': eq.serial_number,  # ← Cambio aquí
            'last_maintenance': eq.maintenances.order_by('-completion_date').first().completion_date if eq.maintenances.exists() else None
        } for eq in equipment_needing_maintenance]
        
        return Response({
            'recent_maintenances': recent_data,
            'equipment_needing_maintenance': equipment_data
        })


class DashboardDepartmentStatsView(APIView):
    """
    Get statistics by department/dependencia.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Equipment by department
        equipment_by_dept = Equipment.objects.values(
            'location'  # Using location as department equivalent
        ).annotate(count=Count('id')).order_by('-count')

        # Maintenances by department (using equipment location)
        maintenances_by_dept = Maintenance.objects.values(
            'equipment__location'
        ).annotate(count=Count('id')).order_by('-count')

        # Incidents by department
        incidents_by_dept = Maintenance.objects.filter(
            is_incident=True
        ).values(
            'equipment__location'
        ).annotate(count=Count('id')).order_by('-count')

        return Response({
            'equipment_by_department': list(equipment_by_dept),
            'maintenances_by_department': list(maintenances_by_dept),
            'incidents_by_department': list(incidents_by_dept),
        })
