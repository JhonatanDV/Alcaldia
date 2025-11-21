import django_filters
from .models import Maintenance


class MaintenanceFilter(django_filters.FilterSet):
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
        ]
