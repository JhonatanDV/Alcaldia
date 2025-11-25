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
from api.models import Dependencia, Sede
from django.contrib.auth import get_user_model
User = get_user_model()


class DashboardStatsView(APIView):
    """
    Estadísticas generales del dashboard
    """
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def _build_filters(self, request):
        """Parse query params into a Q-friendly filter dict."""
        filters = {}
        start = request.query_params.get('start_date')
        end = request.query_params.get('end_date')
        if start:
            filters['scheduled_date__gte'] = start
        if end:
            filters['scheduled_date__lte'] = end

        sede = request.query_params.get('sede')
        if sede:
            filters['sede_rel__nombre'] = sede

        dependencia = request.query_params.get('dependencia')
        if dependencia:
            filters['dependencia_rel__nombre'] = dependencia

        maintenance_type = request.query_params.get('maintenance_type')
        if maintenance_type:
            filters['maintenance_type'] = maintenance_type

        technician = request.query_params.get('technician')
        if technician and technician.isdigit():
            filters['technician__id'] = int(technician)
        return filters

    def get(self, request):
        """
        Retorna estadísticas generales del sistema
        """
        # Debug: Log authentication info
        print("=== DASHBOARD STATS VIEW DEBUG ===")
        print(f"User authenticated: {request.user.is_authenticated}")
        print(f"User: {request.user}")
        auth_header = request.headers.get('Authorization')
        auth_preview = (auth_header[:50] + '...') if auth_header else 'NOT PRESENT'
        print(f"Auth header: {auth_preview}")
        origin = request.headers.get('Origin') or request.headers.get('origin')
        print(f"Origin header: {origin}")
        
        # Estadísticas generales
        filters = self._build_filters(request)

        total_maintenances = Maintenance.objects.filter(**filters).count() if filters else Maintenance.objects.count()
        total_equipment = Equipment.objects.count()
        total_reports = Maintenance.objects.filter(**filters).filter(custom_reports__isnull=False).distinct().count() if filters else Maintenance.objects.filter(custom_reports__isnull=False).distinct().count()
        total_incidents = Incident.objects.count()
        
        # NOTE: breakdowns by status/type have been removed from the simplified dashboard API
        
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
        filters = DashboardStatsView()._build_filters(request)
        # Mantenimientos por mes (últimos 12 meses)
        today = timezone.now()
        maintenances_per_month = []
        
        for i in range(11, -1, -1):
            month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            
            q = Maintenance.objects.filter(scheduled_date__gte=month_start, scheduled_date__lt=month_end)
            if filters:
                q = q.filter(**filters)
            count = q.count()
            
            maintenances_per_month.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })
        
        # Equipos con más mantenimientos
        equipment_q = Equipment.objects.annotate(maintenance_count=Count('maintenances'))
        if filters:
            # filter equipments by maintenances matching filters
            equipment_q = equipment_q.filter(maintenances__in=Maintenance.objects.filter(**filters)).distinct()
        equipment_most_maintenances = equipment_q.order_by('-maintenance_count')[:10]
        
        equipment_data = [{
            'equipment_name': eq.name,
            'equipment_serial': eq.serial_number,  # ← Cambio aquí
            'maintenance_count': eq.maintenance_count
        } for eq in equipment_most_maintenances]
        
        # Note: we no longer return maintenance-by-type breakdown in the simplified charts API
        return Response({
            'maintenances_per_month': maintenances_per_month,
            'equipment_most_maintenances': equipment_data,
        })


class DashboardRecentActivityView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Actividad reciente del dashboard
        """
        filters = DashboardStatsView()._build_filters(request)
        # Mantenimientos recientes
        recent_q = Maintenance.objects.select_related('equipment', 'technician').order_by('-scheduled_date')
        if filters:
            recent_q = recent_q.filter(**filters)
        recent_maintenances = recent_q[:10]
        
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


class FilterOptionsView(APIView):
    """Return distinct values for dashboard filter dropdowns."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sedes = list(Sede.objects.filter().values_list('nombre', flat=True).distinct())
        dependencias = list(Dependencia.objects.filter().values_list('nombre', flat=True).distinct())
        maintenance_types = [t[0] for t in Maintenance.MAINTENANCE_TYPES]
        statuses = [s[0] for s in Maintenance.STATUS_CHOICES]
        technicians = list(User.objects.filter(is_active=True).values('id', 'first_name', 'last_name'))

        techs = [{'id': t['id'], 'name': f"{t['first_name']} {t['last_name']}".strip()} for t in technicians]

        return Response({
            'sedes': sedes,
            'dependencias': dependencias,
            'maintenance_types': maintenance_types,
            'statuses': statuses,
            'technicians': techs,
        })
