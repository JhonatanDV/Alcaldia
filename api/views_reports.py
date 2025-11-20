"""
Example integration of the new PDF generation system in Django views.
This file shows how to use the ReportLab-based PDF generator with parameterizable headers.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from io import BytesIO

from api.models import Maintenance, Report
from api.reports import get_report_generator


# Example 1: Generate PDF with default configuration
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_maintenance_report_default(request, maintenance_id):
    """
    Generate a maintenance report PDF with default header configuration.
    
    Usage:
        POST /api/maintenance/{maintenance_id}/report/
    
    Returns:
        JSON with report_id and pdf_url
    """
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)
    
    try:
        # Generate PDF with default configuration
        generator = get_report_generator('reportlab')
        pdf_buffer = generator.generate(maintenance)
        
        # Create Report record
        report = Report.objects.create(
            maintenance=maintenance,
            generated_by=request.user,
            report_data={'generated_at': timezone.now().isoformat()},
            file_size=len(pdf_buffer.getvalue()),
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        # Save PDF to storage (MinIO)
        filename = f'maintenance_{maintenance_id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        report.pdf_file.save(filename, pdf_buffer)
        
        return Response({
            'status': 'success',
            'report_id': report.id,
            'pdf_url': report.pdf_file.url,
            'file_size': report.file_size,
            'expires_at': report.expires_at
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# Example 2: Generate PDF with custom header configuration
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_maintenance_report_custom(request, maintenance_id):
    """
    Generate a maintenance report PDF with custom header configuration.
    
    Usage:
        POST /api/maintenance/{maintenance_id}/report/custom/
        Body: {
            "header_config": {
                "codigo": "GTI-F-015",
                "version": "04",
                "vigencia": "15-Nov-2025",
                "organization": "ALCALDÍA DE PASTO",
                "department": "GESTIÓN DE TI",
                "logo_path": "/path/to/logo.png"
            }
        }
    
    Returns:
        JSON with report_id and pdf_url
    """
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)
    
    try:
        # Get custom header configuration from request
        header_config = request.data.get('header_config', {})
        
        # Validate and set defaults
        default_config = {
            'organization': 'ALCALDÍA DE PASTO',
            'department': 'GESTIÓN DE TECNOLOGÍAS DE LA INFORMACIÓN',
            'codigo': 'GTI-F-015' if maintenance.maintenance_type == 'computer' else 'GTI-F-016',
            'version': '03' if maintenance.maintenance_type == 'computer' else '02',
            'vigencia': '18-Jul-19'
        }
        
        # Merge with user config
        final_config = {**default_config, **header_config}
        
        # Generate PDF with custom configuration
        generator = get_report_generator('reportlab', final_config)
        pdf_buffer = generator.generate(maintenance)
        
        # Create Report record
        report = Report.objects.create(
            maintenance=maintenance,
            generated_by=request.user,
            report_data={
                'header_config': final_config,
                'generated_at': timezone.now().isoformat()
            },
            file_size=len(pdf_buffer.getvalue()),
            expires_at=timezone.now() + timedelta(days=30)
        )
        
        # Save PDF to storage
        filename = f'maintenance_{maintenance_id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        report.pdf_file.save(filename, pdf_buffer)
        
        return Response({
            'status': 'success',
            'report_id': report.id,
            'pdf_url': report.pdf_file.url,
            'file_size': report.file_size,
            'header_config': final_config,
            'expires_at': report.expires_at
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# Example 3: Download PDF directly without saving to database
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_maintenance_report(request, maintenance_id):
    """
    Download a maintenance report PDF directly without saving to database.
    
    Usage:
        GET /api/maintenance/{maintenance_id}/download/
        Query params (optional):
            - codigo: Form code (e.g., GTI-F-015)
            - version: Version number (e.g., 03)
            - vigencia: Validity date (e.g., 18-Jul-19)
    
    Returns:
        PDF file as attachment
    """
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)
    
    try:
        # Get header configuration from query parameters
        header_config = {}
        if request.query_params.get('codigo'):
            header_config['codigo'] = request.query_params.get('codigo')
        if request.query_params.get('version'):
            header_config['version'] = request.query_params.get('version')
        if request.query_params.get('vigencia'):
            header_config['vigencia'] = request.query_params.get('vigencia')
        
        # Generate PDF
        generator = get_report_generator('reportlab', header_config if header_config else None)
        pdf_buffer = generator.generate(maintenance)
        
        # Return as file download
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="maintenance_{maintenance_id}.pdf"'
        
        return response
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# Example 4: Preview PDF in browser
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def preview_maintenance_report(request, maintenance_id):
    """
    Preview a maintenance report PDF in the browser.
    
    Usage:
        GET /api/maintenance/{maintenance_id}/preview/
    
    Returns:
        PDF file for inline viewing
    """
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)
    
    try:
        # Generate PDF with default configuration
        generator = get_report_generator('reportlab')
        pdf_buffer = generator.generate(maintenance)
        
        # Return as inline PDF
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="maintenance_{maintenance_id}_preview.pdf"'
        
        return response
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# Example 5: Batch generation for multiple maintenances
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_generate_reports(request):
    """
    Generate reports for multiple maintenance records.
    
    Usage:
        POST /api/maintenance/reports/batch/
        Body: {
            "maintenance_ids": [1, 2, 3, 4, 5],
            "header_config": {
                "codigo": "GTI-F-015",
                "version": "03"
            }
        }
    
    Returns:
        JSON with list of generated report URLs
    """
    maintenance_ids = request.data.get('maintenance_ids', [])
    header_config = request.data.get('header_config', {})
    
    if not maintenance_ids:
        return Response({
            'status': 'error',
            'message': 'No maintenance IDs provided'
        }, status=400)
    
    results = []
    errors = []
    
    for maintenance_id in maintenance_ids:
        try:
            maintenance = Maintenance.objects.get(id=maintenance_id)
            
            # Adjust header config based on maintenance type
            config = header_config.copy()
            if not config.get('codigo'):
                config['codigo'] = 'GTI-F-015' if maintenance.maintenance_type == 'computer' else 'GTI-F-016'
            
            # Generate PDF
            generator = get_report_generator('reportlab', config)
            pdf_buffer = generator.generate(maintenance)
            
            # Create Report record
            report = Report.objects.create(
                maintenance=maintenance,
                generated_by=request.user,
                report_data={'header_config': config},
                file_size=len(pdf_buffer.getvalue()),
                expires_at=timezone.now() + timedelta(days=30)
            )
            
            # Save PDF
            filename = f'maintenance_{maintenance_id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            report.pdf_file.save(filename, pdf_buffer)
            
            results.append({
                'maintenance_id': maintenance_id,
                'report_id': report.id,
                'pdf_url': report.pdf_file.url,
                'status': 'success'
            })
            
        except Maintenance.DoesNotExist:
            errors.append({
                'maintenance_id': maintenance_id,
                'error': 'Maintenance not found'
            })
        except Exception as e:
            errors.append({
                'maintenance_id': maintenance_id,
                'error': str(e)
            })
    
    return Response({
        'status': 'completed',
        'total': len(maintenance_ids),
        'success': len(results),
        'failed': len(errors),
        'results': results,
        'errors': errors
    })


# Example 6: Get report with custom configuration for specific format
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_computer_maintenance_report(request, maintenance_id):
    """
    Generate Formato 1: Computer Equipment Maintenance Report (GTI-F-015).
    
    Usage:
        POST /api/maintenance/{maintenance_id}/report/computer/
    """
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)
    
    # Ensure it's a computer maintenance
    if maintenance.maintenance_type != 'computer':
        return Response({
            'status': 'error',
            'message': 'This maintenance is not for computer equipment'
        }, status=400)
    
    try:
        # Computer-specific header configuration
        header_config = {
            'codigo': 'GTI-F-015',
            'version': '03',
            'vigencia': '18-Jul-19',
            'organization': 'ALCALDÍA DE PASTO',
            'department': 'GESTIÓN DE TECNOLOGÍAS DE LA INFORMACIÓN'
        }
        
        generator = get_report_generator('reportlab', header_config)
        pdf_buffer = generator.generate(maintenance)
        
        # Save report
        report = Report.objects.create(
            maintenance=maintenance,
            generated_by=request.user,
            report_data={'header_config': header_config, 'format': 'GTI-F-015'},
            file_size=len(pdf_buffer.getvalue())
        )
        
        filename = f'computer_maintenance_{maintenance_id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        report.pdf_file.save(filename, pdf_buffer)
        
        return Response({
            'status': 'success',
            'format': 'GTI-F-015',
            'report_id': report.id,
            'pdf_url': report.pdf_file.url
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_printer_scanner_report(request, maintenance_id):
    """
    Generate Formato 2: Printer and Scanner Maintenance Report (GTI-F-016).
    
    Usage:
        POST /api/maintenance/{maintenance_id}/report/printer-scanner/
    """
    maintenance = get_object_or_404(Maintenance, id=maintenance_id)
    
    # Ensure it's a printer/scanner maintenance
    if maintenance.maintenance_type != 'printer_scanner':
        return Response({
            'status': 'error',
            'message': 'This maintenance is not for printer/scanner equipment'
        }, status=400)
    
    try:
        # Printer/Scanner-specific header configuration
        header_config = {
            'codigo': 'GTI-F-016',
            'version': '02',
            'vigencia': '18-Jul-19',
            'organization': 'ALCALDÍA DE PASTO',
            'department': 'GESTIÓN DE TECNOLOGÍAS DE LA INFORMACIÓN'
        }
        
        generator = get_report_generator('reportlab', header_config)
        pdf_buffer = generator.generate(maintenance)
        
        # Save report
        report = Report.objects.create(
            maintenance=maintenance,
            generated_by=request.user,
            report_data={'header_config': header_config, 'format': 'GTI-F-016'},
            file_size=len(pdf_buffer.getvalue())
        )
        
        filename = f'printer_scanner_maintenance_{maintenance_id}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        report.pdf_file.save(filename, pdf_buffer)
        
        return Response({
            'status': 'success',
            'format': 'GTI-F-016',
            'report_id': report.id,
            'pdf_url': report.pdf_file.url
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# URL Configuration (add to urls.py)
"""
from django.urls import path
from .views_reports import (
    generate_maintenance_report_default,
    generate_maintenance_report_custom,
    download_maintenance_report,
    preview_maintenance_report,
    batch_generate_reports,
    generate_computer_maintenance_report,
    generate_printer_scanner_report
)

urlpatterns = [
    # Default generation
    path('maintenance/<int:maintenance_id>/report/', 
         generate_maintenance_report_default, 
         name='generate_report_default'),
    
    # Custom header configuration
    path('maintenance/<int:maintenance_id>/report/custom/', 
         generate_maintenance_report_custom, 
         name='generate_report_custom'),
    
    # Direct download
    path('maintenance/<int:maintenance_id>/download/', 
         download_maintenance_report, 
         name='download_report'),
    
    # Preview in browser
    path('maintenance/<int:maintenance_id>/preview/', 
         preview_maintenance_report, 
         name='preview_report'),
    
    # Batch generation
    path('maintenance/reports/batch/', 
         batch_generate_reports, 
         name='batch_generate_reports'),
    
    # Format-specific generation
    path('maintenance/<int:maintenance_id>/report/computer/', 
         generate_computer_maintenance_report, 
         name='generate_computer_report'),
    
    path('maintenance/<int:maintenance_id>/report/printer-scanner/', 
         generate_printer_scanner_report, 
         name='generate_printer_scanner_report'),
]
"""
