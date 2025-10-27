from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import Equipment, Maintenance, Report
import uuid

class ReportGenerator:
    def __init__(self, template_name='reports/equipment_report.html'):
        self.template_name = template_name

    def generate_report(self, context):
        """
        Generate PDF report from context data
        """
        self.validate_data(context)

        # Render HTML template
        html_content = self.render_template(context)

        # Convert HTML to PDF (placeholder - WeasyPrint not available)
        pdf_bytes = self.convert_html_to_pdf(html_content)

        return pdf_bytes

    def render_template(self, context):
        """
        Render Django template with context
        """
        return render_to_string(self.template_name, context)

    def convert_html_to_pdf(self, html_content):
        """
        Convert HTML string to PDF bytes using xhtml2pdf
        """
        from xhtml2pdf import pisa
        from io import BytesIO
        import requests
        from django.conf import settings

        def fetch_resources(uri, rel):
            """
            Callback to fetch external resources like images from MinIO
            """
            if uri.startswith('/media/'):
                # Map local media paths to MinIO URLs
                if 'maintenance_photos' in uri:
                    bucket = settings.MINIO_BUCKET_NAME_PHOTOS
                elif 'maintenance_signatures' in uri:
                    bucket = settings.MINIO_BUCKET_NAME_SIGNATURES
                elif 'maintenance_second_signatures' in uri:
                    bucket = settings.MINIO_BUCKET_NAME_SIGNATURES  # Same bucket
                else:
                    return uri
                key = uri.split('/media/', 1)[1]
                minio_uri = f"{settings.MINIO_ENDPOINT}/{bucket}/{key}"

                try:
                    response = requests.get(minio_uri, timeout=10)
                    if response.status_code == 200:
                        return BytesIO(response.content)
                except Exception as e:
                    print(f"Error fetching resource {minio_uri}: {e}")
            elif uri.startswith('http://') or uri.startswith('https://'):
                try:
                    response = requests.get(uri, timeout=10)
                    if response.status_code == 200:
                        return BytesIO(response.content)
                except Exception as e:
                    print(f"Error fetching resource {uri}: {e}")
            return uri
        
        # Create PDF from HTML
        pdf_file = BytesIO()
        pisa_status = pisa.CreatePDF(
            html_content,
            dest=pdf_file,
            link_callback=fetch_resources
        )
        
        if pisa_status.err:
            raise ValueError("Error generating PDF")
        
        pdf_bytes = pdf_file.getvalue()
        return pdf_bytes

    def validate_data(self, context):
        """
        Validate required data for report generation
        """
        required_keys = ['equipment', 'maintenances', 'start_date', 'end_date']
        for key in required_keys:
            if key not in context:
                raise ValueError(f"Missing required context key: {key}")

def generate_equipment_report(equipment_id, start_date, end_date, user):
    """
    Service function to generate equipment maintenance report
    """
    # Fetch equipment
    equipment = Equipment.objects.get(id=equipment_id)

    # Fetch maintenances in date range
    maintenances = Maintenance.objects.filter(
        equipment=equipment,
        maintenance_date=start_date  # Filter by exact date
    ).order_by('maintenance_date').prefetch_related('photos', 'signature', 'second_signature')

    # Ensure maintenances have activities populated
    for maintenance in maintenances:
        # Handle case where activities is stored as string '{}'
        activities_dict = maintenance.activities
        if isinstance(activities_dict, str):
            import json
            try:
                activities_dict = json.loads(activities_dict)
            except:
                activities_dict = {}

        if not activities_dict or activities_dict == {}:
            if maintenance.maintenance_type == 'computer':
                activities_dict = {
                    # RUTINA DE HARDWARE
                    'Limpieza interna de la torre': None,
                    'Limpieza del teclado': None,
                    'Limpieza del monitor': None,
                    'Verificación de cables de poder y de datos': None,
                    'Ajuste de tarjetas (Memoria - Video - Red)': None,
                    'Lubricación del ventilador de la torre': None,
                    'Lubricación del ventilador del procesador': None,
                    # RUTINA DE SOFTWARE
                    'Crear partición de datos': None,
                    'Mover información a partición de datos': None,
                    'Reinstalar sistema operativo': None,
                    'Instalar antivirus': None,
                    'Análisis en busca de software malicioso': None,
                    'Diagnosticar funcionamiento aplicaciones instaladas': None,
                    'Suspender actualizaciones automáticas S.O.': None,
                    'Instalar programas esenciales (ofimática, grabador de discos)': None,
                    'Configurar usuarios administrador local': None,
                    'Modificar contraseña de administrador': None,
                    'Configurar nombre equipo': None,
                    'El equipo tiene estabilizador': None,
                    'El escritorio está limpio': None,
                    'Desactivar aplicaciones al inicio de Windows': None,
                    'Configurar página de inicio navegador': None,
                    'Configurar fondo de pantalla institucional': None,
                    'Configurar protector de pantalla institucional': None,
                    'Verificar funcionamiento general': None,
                    'Inventario de equipo': None,
                    'Limpieza de registros y eliminación de archivos temporales': None,
                    'Creación Punto de Restauración': None,
                    'Verificar espacio en disco': None,
                    'Desactivar software no autorizado': None,
                    'Analizar disco duro': None,
                    'El usuario de Windows tiene contraseña': None,
                    'OBSERVACIONES GENERALES': None,
                    'OBSERVACIONES SEGURIDAD DE LA INFORMACIÓN': None
                }
            else:  # printer_scanner
                activities_dict = {
                    # RUTINA DE ESCÁNER
                    'Limpieza general': None,
                    'Alineación de papel': None,
                    'Configuración del equipo': None,
                    'Pruebas de funcionamiento': None,
                    # RUTINA DE IMPRESORAS
                    'Limpieza de carcasa': None,
                    'Limpieza tóner': None,
                    'Limpieza tarjeta lógica': None,
                    'Limpieza de sensores': None,
                    'Limpieza de rodillo': None,
                    'Limpieza de correas dentadas o guías': None,
                    'Limpieza de ventiladores': None,
                    'Limpieza de cabezal impresora matriz de punto e inyección tinta': None,
                    'Limpieza de engranaje': None,
                    'Limpieza de fusor': None,
                    'Limpieza tarjeta de poder': None,
                    'Alineación de rodillos alimentación de papel': None,
                    'Configuración del equipo': None,
                    'Pruebas de funcionamiento': None,
                    'DIAGNÓSTICO': None,
                    'OBSERVACIONES ADICIONALES': None
                }
            maintenance.activities = activities_dict
            maintenance.save()

    # Prepare context
    context = {
        'equipment': equipment,
        'maintenances': maintenances,
        'start_date': start_date,
        'end_date': end_date,
        'generated_at': timezone.now(),
        'generated_by': user.get_full_name() or user.username
    }

    # Generate PDF
    generator = ReportGenerator()
    pdf_bytes = generator.generate_report(context)

    # Find a maintenance for the equipment on the given date
    maintenance = Maintenance.objects.filter(
        equipment=equipment,
        maintenance_date=start_date
    ).first()

    if not maintenance:
        raise ValueError(f"No maintenance found for equipment {equipment.code} on {start_date}")

    # Check if report already exists for this maintenance
    try:
        report = Report.objects.get(maintenance=maintenance)
        # Update existing report
        report.generated_by = user
        report.report_data = {
            'equipment_id': equipment_id,
            'start_date': str(start_date),
            'end_date': str(end_date)
        }
        report.expires_at = timezone.now() + timedelta(hours=1)
        report.file_size = len(pdf_bytes)

        # Save PDF file to MinIO
        from django.core.files.base import ContentFile
        from core.storage import MaintenanceReportStorage
        filename = f"report_{report.id}_{uuid.uuid4()}.pdf"
        storage = MaintenanceReportStorage()
        storage.save(filename, ContentFile(pdf_bytes))
        report.pdf_file = filename
        report.save()

    except Report.DoesNotExist:
        # Create new report
        report = Report.objects.create(
            maintenance=maintenance,
            generated_by=user,
            report_data={
                'equipment_id': equipment_id,
                'start_date': str(start_date),
                'end_date': str(end_date)
            },
            expires_at=timezone.now() + timedelta(hours=1),
            file_size=len(pdf_bytes)
        )

        # Save PDF file to MinIO
        from django.core.files.base import ContentFile
        from core.storage import MaintenanceReportStorage
        filename = f"report_{report.id}_{uuid.uuid4()}.pdf"
        storage = MaintenanceReportStorage()
        storage.save(filename, ContentFile(pdf_bytes))
        report.pdf_file = filename
        report.save()

    return report
