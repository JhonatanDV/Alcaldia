import django_filters
from .models import Maintenance

class MaintenanceFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='maintenance_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='maintenance_date', lookup_expr='lte')
    performed_by = django_filters.CharFilter(field_name='performed_by', lookup_expr='icontains')
    equipment_code = django_filters.CharFilter(field_name='equipment__code', lookup_expr='icontains')
    equipment_location = django_filters.CharFilter(field_name='equipment__location', lookup_expr='icontains')
    sede = django_filters.CharFilter(field_name='sede', lookup_expr='icontains')
    dependencia = django_filters.CharFilter(field_name='dependencia', lookup_expr='icontains')
    oficina = django_filters.CharFilter(field_name='oficina', lookup_expr='icontains')
    placa = django_filters.CharFilter(field_name='placa', lookup_expr='icontains')
    maintenance_type = django_filters.CharFilter(field_name='maintenance_type', lookup_expr='exact')
    is_incident = django_filters.BooleanFilter(field_name='is_incident')

    class Meta:
        model = Maintenance
        fields = [
            'equipo', 'fecha_mantenimiento', 'tecnico_responsable', 'equipment_code',
            'equipment_location', 'date_from', 'date_to', 'sede', 'dependencia',
            'oficina', 'placa', 'maintenance_type', 'is_incident'
        ]
