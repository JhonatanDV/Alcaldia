"""
PDF packaging views for creating ZIP files with multiple PDFs.
"""

import zipfile
from io import BytesIO
from datetime import datetime
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Maintenance, Incident, Equipment
from .reports import get_report_generator
from .filters import MaintenanceFilter


class PackageMaintenancePDFsView(APIView):
    """
    Package multiple maintenance PDFs into a ZIP file.
    Supports filtering by sede, dependencia, subdependencia, dates, etc.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        maintenance_ids = request.data.get('maintenance_ids', [])
        filters = request.data.get('filters', {})
        
        # Si se proporcionan IDs específicos, usar esos
        if maintenance_ids:
            maintenances = Maintenance.objects.filter(id__in=maintenance_ids)
        # Si se proporcionan filtros, aplicarlos
        elif filters:
            queryset = Maintenance.objects.all()
            filterset = MaintenanceFilter(filters, queryset=queryset)
            maintenances = filterset.qs
        else:
            return Response({
                'error': 'Se requiere maintenance_ids o filters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not maintenances.exists():
            return Response({
                'error': 'No se encontraron mantenimientos'
            }, status=status.HTTP_404_NOT_FOUND)

        # Create BytesIO buffer for ZIP
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for maintenance in maintenances:
                try:
                    # Generate PDF
                    generator = get_report_generator('reportlab')
                    pdf_buffer = generator.generate(maintenance)
                    
                    # Add to ZIP with descriptive filename
                    placa = maintenance.placa or maintenance.equipment.serial_number or maintenance.id
                    fecha = maintenance.scheduled_date.strftime('%Y%m%d')
                    filename = f"mantenimiento_{placa}_{fecha}.pdf"
                    zip_file.writestr(filename, pdf_buffer.getvalue())
                    
                except Exception as e:
                    print(f"Error generando PDF para mantenimiento {maintenance.id}: {str(e)}")
                    continue
        
        # Prepare response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="mantenimientos_{timestamp}.zip"'
        
        return response


class PackageIncidentPDFsView(APIView):
    """
    Package multiple incident PDFs into a ZIP file.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        incident_ids = request.data.get('incident_ids', [])
        
        if not incident_ids:
            return Response({
                'error': 'incident_ids is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for incident_id in incident_ids:
                try:
                    incident = Incident.objects.get(id=incident_id)
                    
                    # Generate PDF
                    pdf_generator = IncidentReportPDF(incident)
                    pdf_buffer = pdf_generator.generate()
                    
                    # Add to ZIP
                    filename = f"incidente_{incident.equipo.placa}_{incident.fecha_reporte.strftime('%Y%m%d')}.pdf"
                    zip_file.writestr(filename, pdf_buffer.getvalue())
                    
                except Incident.DoesNotExist:
                    continue
        
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="incidentes_package.zip"'
        
        return response


class PackageEquipmentPDFsView(APIView):
    """
    Package all PDFs related to an equipment (maintenances + incidents).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        equipment_id = request.data.get('equipment_id')
        
        if not equipment_id:
            return Response({
                'error': 'equipment_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            equipment = Equipment.objects.get(id=equipment_id)
        except Equipment.DoesNotExist:
            return Response({
                'error': 'Equipment not found'
            }, status=status.HTTP_404_NOT_FOUND)

        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add maintenance PDFs
            maintenances = Maintenance.objects.filter(equipo=equipment)
            for maintenance in maintenances:
                pdf_generator = MaintenanceReportPDF(maintenance)
                pdf_buffer = pdf_generator.generate()
                filename = f"mantenimiento_{maintenance.fecha_mantenimiento.strftime('%Y%m%d')}.pdf"
                zip_file.writestr(filename, pdf_buffer.getvalue())
            
            # Add incident PDFs
            incidents = Incident.objects.filter(equipo=equipment)
            for incident in incidents:
                pdf_generator = IncidentReportPDF(incident)
                pdf_buffer = pdf_generator.generate()
                filename = f"incidente_{incident.fecha_reporte.strftime('%Y%m%d')}.pdf"
                zip_file.writestr(filename, pdf_buffer.getvalue())
        
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="equipo_{equipment.placa}_historico.zip"'
        
        return response


class PackageDateRangePDFsView(APIView):
    """
    Package PDFs for a specific date range.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        include_maintenances = request.data.get('include_maintenances', True)
        include_incidents = request.data.get('include_incidents', True)
        
        if not start_date or not end_date:
            return Response({
                'error': 'start_date and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)

        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            if include_maintenances:
                maintenances = Maintenance.objects.filter(
                    fecha_mantenimiento__gte=start_date,
                    fecha_mantenimiento__lte=end_date
                )
                for maintenance in maintenances:
                    pdf_generator = MaintenanceReportPDF(maintenance)
                    pdf_buffer = pdf_generator.generate()
                    filename = f"mantenimiento_{maintenance.equipo.placa}_{maintenance.fecha_mantenimiento.strftime('%Y%m%d')}.pdf"
                    zip_file.writestr(filename, pdf_buffer.getvalue())
            
            if include_incidents:
                incidents = Incident.objects.filter(
                    fecha_reporte__gte=start_date,
                    fecha_reporte__lte=end_date
                )
                for incident in incidents:
                    pdf_generator = IncidentReportPDF(incident)
                    pdf_buffer = pdf_generator.generate()
                    filename = f"incidente_{incident.equipo.placa}_{incident.fecha_reporte.strftime('%Y%m%d')}.pdf"
                    zip_file.writestr(filename, pdf_buffer.getvalue())
        
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="reportes_{start_date}_{end_date}.zip"'
        
        return response
