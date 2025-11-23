import django_filters
from django.db.models import Q
from .models import Maintenance


class MaintenanceFilter(django_filters.FilterSet):
    # Date range filters
    scheduled_date_from = django_filters.DateFilter(field_name='scheduled_date', lookup_expr='gte')
    scheduled_date_to = django_filters.DateFilter(field_name='scheduled_date', lookup_expr='lte')
    completion_date_from = django_filters.DateFilter(field_name='completion_date', lookup_expr='gte')
    completion_date_to = django_filters.DateFilter(field_name='completion_date', lookup_expr='lte')
    created_at_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_at_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    # Text search filter
    search = django_filters.CharFilter(method='filter_search')

    # Equipment-related filters
    equipment_name = django_filters.CharFilter(field_name='equipment__name', lookup_expr='icontains')
    equipment_serial = django_filters.CharFilter(field_name='equipment__serial_number', lookup_expr='icontains')
    equipment_brand = django_filters.CharFilter(field_name='equipment__brand', lookup_expr='icontains')
    equipment_model = django_filters.CharFilter(field_name='equipment__model', lookup_expr='icontains')
    equipment_location = django_filters.CharFilter(field_name='equipment__location', lookup_expr='icontains')
    equipment_dependencia = django_filters.CharFilter(field_name='equipment__dependencia', lookup_expr='icontains')

    # Filtros jerárquicos por ID (relaciones ForeignKey)
    sede_id = django_filters.NumberFilter(field_name='sede_rel__id')
    dependencia_id = django_filters.NumberFilter(field_name='dependencia_rel__id')
    subdependencia_id = django_filters.NumberFilter(field_name='subdependencia__id')
    
    # Filtros por nombre (para búsquedas de texto)
    sede_nombre = django_filters.CharFilter(field_name='sede_rel__nombre', lookup_expr='icontains')
    dependencia_nombre = django_filters.CharFilter(field_name='dependencia_rel__nombre', lookup_expr='icontains')
    subdependencia_nombre = django_filters.CharFilter(field_name='subdependencia__nombre', lookup_expr='icontains')

    # Maintenance-specific filters (legacy)
    sede = django_filters.CharFilter(field_name='sede', lookup_expr='icontains')
    oficina = django_filters.CharFilter(field_name='oficina', lookup_expr='icontains')
    placa = django_filters.CharFilter(field_name='placa', lookup_expr='icontains')

    class Meta:
        model = Maintenance
        fields = [
            'equipment',
            'maintenance_type',
            'status',
            'technician',
            'scheduled_date',
            'completion_date',
            'dependencia',
            'ubicacion',
            'sede',
            'oficina',
            'placa',
            'sede_id',
            'dependencia_id',
            'subdependencia_id',
        ]

    def filter_search(self, queryset, name, value):
        """Custom search method that searches across multiple fields"""
        return queryset.filter(
            Q(equipment__name__icontains=value) |
            Q(equipment__serial_number__icontains=value) |
            Q(equipment__brand__icontains=value) |
            Q(equipment__model__icontains=value) |
            Q(equipment__location__icontains=value) |
            Q(equipment__dependencia__icontains=value) |
            Q(description__icontains=value) |
            Q(observations__icontains=value) |
            Q(sede__icontains=value) |
            Q(sede_rel__nombre__icontains=value) |
            Q(dependencia_rel__nombre__icontains=value) |
            Q(subdependencia__nombre__icontains=value) |
            Q(oficina__icontains=value) |
            Q(placa__icontains=value) |
            Q(technician__username__icontains=value) |
            Q(technician__first_name__icontains=value) |
            Q(technician__last_name__icontains=value)
        )
