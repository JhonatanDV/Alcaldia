import django_filters
from .models import Maintenance

class MaintenanceFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='maintenance_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='maintenance_date', lookup_expr='lte')
    performed_by = django_filters.CharFilter(field_name='performed_by', lookup_expr='icontains')
    equipment_code = django_filters.CharFilter(field_name='equipment__code', lookup_expr='icontains')
    equipment_location = django_filters.CharFilter(field_name='equipment__location', lookup_expr='icontains')

    class Meta:
        model = Maintenance
        fields = ['equipment', 'maintenance_date', 'performed_by', 'equipment_code', 'equipment_location', 'date_from', 'date_to']
