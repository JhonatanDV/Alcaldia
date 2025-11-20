"""
PDF packaging views - create ZIP files of multiple reports.
"""

import os
import zipfile
from io import BytesIO
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from api.models import Report
from api.permissions import IsAdmin
from django.conf import settings


@api_view(['POST'])
@permission_classes([IsAdmin])
def package_reports(request):
    """
    Package multiple PDF reports into a ZIP file.
    
    Body: {
        "report_ids": [1, 2, 3, 4],
        "filename": "reportes_mayo_2024.zip"  # Optional
    }
    
    Returns: ZIP file download
    """
    report_ids = request.data.get('report_ids', [])
    custom_filename = request.data.get('filename', 'reportes.zip')
    
    if not report_ids or not isinstance(report_ids, list):
        return Response(
            {'error': 'report_ids must be a non-empty list'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Ensure filename ends with .zip
    if not custom_filename.endswith('.zip'):
        custom_filename += '.zip'
    
    # Get reports
    reports = Report.objects.filter(id__in=report_ids)
    
    if not reports.exists():
        return Response(
            {'error': 'No reports found with the provided IDs'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Create ZIP file in memory
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for report in reports:
            if report.pdf_file:
                try:
                    # Get PDF file path
                    pdf_path = report.pdf_file.path if hasattr(report.pdf_file, 'path') else None
                    
                    if pdf_path and os.path.exists(pdf_path):
                        # Read from filesystem
                        with open(pdf_path, 'rb') as pdf:
                            pdf_content = pdf.read()
                    else:
                        # Read from MinIO/S3 storage
                        pdf_content = report.pdf_file.read()
                    
                    # Generate filename for the PDF inside ZIP
                    # Format: REPORTE_{maintenance_id}_{equipment_placa}_{date}.pdf
                    maintenance = report.maintenance
                    equipment_placa = maintenance.equipment.placa if maintenance.equipment else 'SIN_PLACA'
                    date_str = maintenance.date.strftime('%Y%m%d') if maintenance.date else 'SIN_FECHA'
                    
                    pdf_filename = f"REPORTE_{maintenance.id}_{equipment_placa}_{date_str}.pdf"
                    
                    # Add to ZIP
                    zip_file.writestr(pdf_filename, pdf_content)
                    
                except Exception as e:
                    # Log error but continue with other files
                    print(f"Error adding report {report.id} to ZIP: {str(e)}")
                    continue
    
    # Check if any files were added
    zip_buffer.seek(0)
    if zip_buffer.getbuffer().nbytes == 0:
        return Response(
            {'error': 'No PDF files could be added to the ZIP'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Return ZIP file
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{custom_filename}"'
    
    return response


@api_view(['POST'])
@permission_classes([IsAdmin])
def package_reports_by_filter(request):
    """
    Package reports by filter criteria.
    
    Body: {
        "date_from": "2024-01-01",
        "date_to": "2024-12-31",
        "dependencia": "SECRETARIA DE SALUD",
        "sede": "SEDE PRINCIPAL",
        "oficina": "OFICINA 101",
        "placa": "TI-001",
        "maintenance_type": "preventivo",
        "filename": "reportes_filtrados.zip"
    }
    
    All filter fields are optional.
    """
    from api.filters import MaintenanceFilter
    from django.db.models import Q
    
    # Get filter parameters
    date_from = request.data.get('date_from')
    date_to = request.data.get('date_to')
    dependencia = request.data.get('dependencia')
    sede = request.data.get('sede')
    oficina = request.data.get('oficina')
    placa = request.data.get('placa')
    maintenance_type = request.data.get('maintenance_type')
    custom_filename = request.data.get('filename', 'reportes_filtrados.zip')
    
    # Build query
    query = Q()
    
    if date_from:
        query &= Q(maintenance__date__gte=date_from)
    if date_to:
        query &= Q(maintenance__date__lte=date_to)
    if dependencia:
        query &= Q(maintenance__equipment__dependencia__icontains=dependencia)
    if sede:
        query &= Q(maintenance__equipment__sede__icontains=sede)
    if oficina:
        query &= Q(maintenance__equipment__oficina__icontains=oficina)
    if placa:
        query &= Q(maintenance__equipment__placa__icontains=placa)
    if maintenance_type:
        query &= Q(maintenance__maintenance_type=maintenance_type)
    
    # Get reports
    reports = Report.objects.filter(query).select_related('maintenance__equipment')
    
    if not reports.exists():
        return Response(
            {'error': 'No reports found matching the filter criteria'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Ensure filename ends with .zip
    if not custom_filename.endswith('.zip'):
        custom_filename += '.zip'
    
    # Create ZIP file in memory
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for report in reports:
            if report.pdf_file:
                try:
                    # Get PDF file path
                    pdf_path = report.pdf_file.path if hasattr(report.pdf_file, 'path') else None
                    
                    if pdf_path and os.path.exists(pdf_path):
                        # Read from filesystem
                        with open(pdf_path, 'rb') as pdf:
                            pdf_content = pdf.read()
                    else:
                        # Read from MinIO/S3 storage
                        pdf_content = report.pdf_file.read()
                    
                    # Generate filename
                    maintenance = report.maintenance
                    equipment_placa = maintenance.equipment.placa if maintenance.equipment else 'SIN_PLACA'
                    date_str = maintenance.date.strftime('%Y%m%d') if maintenance.date else 'SIN_FECHA'
                    
                    pdf_filename = f"REPORTE_{maintenance.id}_{equipment_placa}_{date_str}.pdf"
                    
                    # Add to ZIP
                    zip_file.writestr(pdf_filename, pdf_content)
                    
                except Exception as e:
                    print(f"Error adding report {report.id} to ZIP: {str(e)}")
                    continue
    
    # Check if any files were added
    zip_buffer.seek(0)
    if zip_buffer.getbuffer().nbytes == 0:
        return Response(
            {'error': 'No PDF files could be added to the ZIP'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Return ZIP file
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{custom_filename}"'
    
    return response


@api_view(['GET'])
@permission_classes([IsAdmin])
def package_info(request):
    """
    Get information about available reports for packaging.
    
    Returns counts by different criteria.
    """
    from django.db.models import Count
    from api.models import Maintenance
    
    total_reports = Report.objects.count()
    
    reports_by_type = Maintenance.objects.values('maintenance_type').annotate(
        count=Count('report')
    )
    
    reports_by_dependency = Maintenance.objects.values('equipment__dependencia').annotate(
        count=Count('report')
    )
    
    return Response({
        'total_reports': total_reports,
        'by_type': list(reports_by_type),
        'by_dependency': list(reports_by_dependency),
    })
