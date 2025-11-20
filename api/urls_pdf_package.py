from django.urls import path
from .views_pdf_package import (
    PackageMaintenancePDFsView,
    PackageIncidentPDFsView,
    PackageEquipmentPDFsView,
    PackageDateRangePDFsView,
)

urlpatterns = [
    path('maintenances/', PackageMaintenancePDFsView.as_view(), name='package-maintenances'),
    path('incidents/', PackageIncidentPDFsView.as_view(), name='package-incidents'),
    path('equipment/', PackageEquipmentPDFsView.as_view(), name='package-equipment'),
    path('date-range/', PackageDateRangePDFsView.as_view(), name='package-date-range'),
]