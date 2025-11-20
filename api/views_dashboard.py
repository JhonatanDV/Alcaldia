"""
Dashboard views with complete statistics and metrics.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .models import Equipment, Maintenance, Report


class DashboardStatsView(APIView):
    """
    Get complete dashboard statistics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Basic counts
        total_equipment = Equipment.objects.count()
        total_maintenances = Maintenance.objects.count()
        total_incidents = Maintenance.objects.filter(is_incident=True).count()
        total_users = User.objects.filter(is_active=True).count()
        total_reports = Report.objects.count()

        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_maintenances = Maintenance.objects.filter(
            maintenance_date__gte=thirty_days_ago
        ).count()
        recent_incidents = Maintenance.objects.filter(
            maintenance_date__gte=thirty_days_ago,
            is_incident=True
        ).count()

        # Equipment status (we'll use a simple approach since no status field exists)
        # For now, consider equipment "in maintenance" if it had maintenance in last 30 days
        equipment_with_recent_maintenance = Equipment.objects.filter(
            maintenances__maintenance_date__gte=thirty_days_ago
        ).distinct().count()

        # Maintenance by type
        maintenance_by_type = Maintenance.objects.values(
            'maintenance_type'
        ).annotate(count=Count('id')).order_by('-count')

        # Incidents by "status" (we'll use a simple approach)
        incidents_by_status = [
            {'estado': 'reportado', 'count': total_incidents}
        ]

        return Response({
            'overview': {
                'total_equipment': total_equipment,
                'total_maintenances': total_maintenances,
                'total_incidents': total_incidents,
                'total_users': total_users,
                'total_reports': total_reports,
                'recent_maintenances': recent_maintenances,
                'recent_incidents': recent_incidents,
            },
            'equipment_status': {
                'total': total_equipment,
                'with_recent_maintenance': equipment_with_recent_maintenance,
            },
            'maintenance_by_type': list(maintenance_by_type),
            'incidents_by_status': incidents_by_status,
        })


class DashboardChartsView(APIView):
    """
    Get data for dashboard charts.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Maintenances per month (last 12 months)
        twelve_months_ago = timezone.now() - timedelta(days=365)
        maintenances_per_month = []

        for i in range(12):
            month_start = timezone.now() - timedelta(days=30 * (11 - i))
            month_end = month_start + timedelta(days=30)
            count = Maintenance.objects.filter(
                maintenance_date__gte=month_start,
                maintenance_date__lt=month_end
            ).count()
            maintenances_per_month.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })

        # Maintenances by technician (performed_by field)
        maintenances_by_tech = Maintenance.objects.values(
            'performed_by'
        ).annotate(count=Count('id')).order_by('-count')[:10]

        # Equipment with most maintenances
        equipment_most_maintenances = Equipment.objects.annotate(
            maintenance_count=Count('maintenances')
        ).order_by('-maintenance_count')[:10].values(
            'code', 'name', 'maintenance_count'
        )

        # Incidents per month
        incidents_per_month = []
        for i in range(12):
            month_start = timezone.now() - timedelta(days=30 * (11 - i))
            month_end = month_start + timedelta(days=30)
            count = Maintenance.objects.filter(
                maintenance_date__gte=month_start,
                maintenance_date__lt=month_end,
                is_incident=True
            ).count()
            incidents_per_month.append({
                'month': month_start.strftime('%b %Y'),
                'count': count
            })

        return Response({
            'maintenances_per_month': maintenances_per_month,
            'maintenances_by_technician': list(maintenances_by_tech),
            'equipment_most_maintenances': list(equipment_most_maintenances),
            'incidents_per_month': incidents_per_month,
        })


class DashboardRecentActivityView(APIView):
    """
    Get recent activity for dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Recent maintenances (last 10)
        recent_maintenances = Maintenance.objects.select_related(
            'equipment'
        ).order_by('-maintenance_date')[:10].values(
            'id', 'equipment__code', 'equipment__name', 'maintenance_type',
            'maintenance_date', 'performed_by', 'is_incident'
        )

        # Recent incidents (last 10) - maintenances marked as incidents
        recent_incidents = Maintenance.objects.select_related(
            'equipment'
        ).filter(is_incident=True).order_by('-maintenance_date')[:10].values(
            'id', 'equipment__code', 'maintenance_type', 'description',
            'maintenance_date', 'performed_by'
        )

        # Equipment needing maintenance (no recent maintenance in 90 days)
        ninety_days_ago = timezone.now() - timedelta(days=90)
        equipment_needing_maintenance = Equipment.objects.exclude(
            maintenances__maintenance_date__gte=ninety_days_ago
        ).distinct()[:10].values(
            'id', 'code', 'name'
        )

        return Response({
            'recent_maintenances': list(recent_maintenances),
            'recent_incidents': list(recent_incidents),
            'equipment_needing_maintenance': list(equipment_needing_maintenance),
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
