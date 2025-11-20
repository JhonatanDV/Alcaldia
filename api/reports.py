"""
ReportGenerator pattern for PDF generation.
This module provides an abstraction for generating different types of reports.
"""

from abc import ABC, abstractmethod
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, 
    Table, TableStyle, PageBreak, KeepTogether, Frame, PageTemplate
)
from reportlab.pdfgen import canvas as pdfgen_canvas
from reportlab.platypus.flowables import Flowable
from django.conf import settings
from .models import Maintenance


class CheckboxFlowable(Flowable):
    """Custom flowable for rendering checkboxes in PDFs."""
    
    def __init__(self, checked=False, size=10):
        Flowable.__init__(self)
        self.checked = checked
        self.size = size
        self.width = size
        self.height = size
    
    def draw(self):
        """Draw a checkbox."""
        self.canv.rect(0, 0, self.size, self.size)
        if self.checked:
            # Draw an X or checkmark
            self.canv.line(2, 2, self.size-2, self.size-2)
            self.canv.line(2, self.size-2, self.size-2, 2)


class PDFHeaderFooter:
    """Class to handle PDF headers and footers with parameterization."""
    
    def __init__(self, header_config=None):
        """
        Initialize header/footer configuration.
        
        Args:
            header_config: Dictionary with header parameters like:
                - title: Main title
                - codigo: Code (e.g., GTI-F-015)
                - version: Version number
                - vigencia: Validity date
                - logo_path: Path to organization logo
        """
        self.config = header_config or {}
    
    def draw_header(self, canvas, doc):
        """Draw header on each page."""
        canvas.saveState()
        
        # Draw logo if provided
        logo_path = self.config.get('logo_path')
        if logo_path:
            try:
                canvas.drawImage(logo_path, 1*cm, letter[1] - 2*cm, width=2*cm, height=2*cm, preserveAspectRatio=True)
            except:
                pass  # If logo fails, continue without it
        
        # Main title
        canvas.setFont('Helvetica-Bold', 11)
        canvas.drawCentredString(letter[0]/2, letter[1] - 1.5*cm, 
                                self.config.get('organization', 'ALCALDÍA DE PASTO'))
        
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawCentredString(letter[0]/2, letter[1] - 2*cm, 
                                self.config.get('department', 'GESTIÓN DE TECNOLOGÍAS DE LA INFORMACIÓN'))
        
        # Code, version, and validity
        canvas.setFont('Helvetica', 8)
        info_y = letter[1] - 2.5*cm
        info_text = f"Código: {self.config.get('codigo', 'N/A')}  |  " \
                   f"Versión: {self.config.get('version', 'N/A')}  |  " \
                   f"Vigencia: {self.config.get('vigencia', 'N/A')}"
        canvas.drawCentredString(letter[0]/2, info_y, info_text)
        
        # Horizontal line
        canvas.setStrokeColor(colors.grey)
        canvas.line(1*cm, letter[1] - 2.8*cm, letter[0] - 1*cm, letter[1] - 2.8*cm)
        
        canvas.restoreState()
    
    def draw_footer(self, canvas, doc):
        """Draw footer on each page."""
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.drawString(1*cm, 1*cm, f"Página {doc.page}")
        canvas.drawRightString(letter[0] - 1*cm, 1*cm, 
                              f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.restoreState()


class ReportGenerator(ABC):
    """Abstract base class for report generators."""

    @abstractmethod
    def generate(self, maintenance: Maintenance) -> BytesIO:
        """Generate a report for the given maintenance."""
        pass


class ReportLabGenerator(ReportGenerator):
    """PDF generator using ReportLab with full format support."""

    def __init__(self, header_config=None):
        """Initialize generator with custom header configuration."""
        self.header_config = header_config or {}
        self.styles = self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for the report."""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#2c5aa0'),
            borderPadding=5,
            backColor=colors.HexColor('#e8f0f8')
        ))
        
        styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='FieldValue',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica'
        ))
        
        return styles

    def generate(self, maintenance: Maintenance) -> BytesIO:
        """Generate PDF based on maintenance type."""
        if maintenance.maintenance_type == 'computer':
            return self._generate_computer_report(maintenance)
        elif maintenance.maintenance_type == 'printer_scanner':
            return self._generate_printer_scanner_report(maintenance)
        else:
            return self._generate_generic_report(maintenance)
    
    def _generate_computer_report(self, maintenance: Maintenance) -> BytesIO:
        """Generate Formato 1: Rutina Mantenimiento Preventivo de Equipos de Cómputo."""
        buffer = BytesIO()
        
        # Configure header
        header_config = {
            'organization': 'ALCALDÍA DE PASTO',
            'department': 'GESTIÓN DE TECNOLOGÍAS DE LA INFORMACIÓN',
            'codigo': 'GTI-F-015',
            'version': '03',
            'vigencia': '18-Jul-19',
            **self.header_config
        }
        
        # Create document with custom header/footer
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=3.5*cm,
            bottomMargin=2*cm,
            leftMargin=2*cm,
            rightMargin=2*cm
        )
        
        story = []
        
        # Title
        title = Paragraph(
            "🖥 FORMATO 1: RUTINA MANTENIMIENTO PREVENTIVO DE EQUIPOS DE CÓMPUTO",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.3*cm))
        
        # Basic Information Section
        basic_info_data = [
            ['Sede:', maintenance.sede or '_' * 40],
            ['Dependencia:', maintenance.dependencia or '_' * 40],
            ['Oficina:', maintenance.oficina or '_' * 40],
            ['Placa Torre (si no tiene, informar identificación):', maintenance.placa or maintenance.equipment.code],
        ]
        
        date_time_data = [
            ['Fecha Mantenimiento:', f"Día {maintenance.maintenance_date.day:02d} / Mes {maintenance.maintenance_date.month:02d} / Año {maintenance.maintenance_date.year}"],
            ['Hora Inicio:', maintenance.hora_inicio.strftime('%H:%M') if maintenance.hora_inicio else '_______',
             'Hora Final:', maintenance.hora_final.strftime('%H:%M') if maintenance.hora_final else '_______']
        ]
        
        for row in basic_info_data:
            table = Table([row], colWidths=[5*cm, 12*cm])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, 0), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(table)
        
        table = Table([date_time_data[0]], colWidths=[4*cm, 13*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(table)
        
        time_table = Table([date_time_data[1]], colWidths=[2.5*cm, 3*cm, 2.5*cm, 3*cm])
        time_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(time_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Hardware Section
        story.append(Paragraph("🔧 RUTINA DE HARDWARE", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*cm))
        
        hardware_activities = [
            'Limpieza interna de la torre',
            'Limpieza del teclado',
            'Limpieza del monitor',
            'Verificación de cables de poder y de datos',
            'Ajuste de tarjetas (Memoria - Video - Red)',
            'Lubricación del ventilador de la torre',
            'Lubricación del ventilador de la fuente',
            'Lubricación del ventilador del procesador',
        ]
        
        hw_table_data = [['Actividad', 'SI', 'N.A.']]
        activities_data = maintenance.activities or {}
        
        for activity in hardware_activities:
            activity_key = activity.lower().replace(' ', '_')
            status = activities_data.get(f'hardware_{activity_key}', '')
            hw_table_data.append([
                activity,
                '☑' if status == 'SI' else '☐',
                '☑' if status == 'N.A.' else '☐'
            ])
        
        hw_table = Table(hw_table_data, colWidths=[12*cm, 2*cm, 2*cm])
        hw_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d0e0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(hw_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Software Section
        story.append(Paragraph("💽 RUTINA DE SOFTWARE", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*cm))
        
        software_activities = [
            'Crear partición de datos',
            'Mover información a partición de datos',
            'Reinstalar sistema operativo',
            'Instalar antivirus',
            'Análisis en busca de software malicioso',
            'Diagnosticar funcionamiento aplicaciones instaladas',
            'Suspender actualizaciones automáticas S.O.',
            'Instalar programas esenciales (ofimática, grabador de discos)',
            'Configurar usuarios administrador local',
            'Modificar contraseña de administrador',
            'Configurar nombre equipo',
            'El equipo tiene estabilizador',
            'El escritorio está limpio',
            'Desactivar aplicaciones al inicio de Windows',
            'Configurar página de inicio navegador',
            'Configurar fondo de pantalla institucional',
            'Configurar protector de pantalla institucional',
            'Verificar funcionamiento general',
            'Inventario de equipo',
            'Limpieza de registros y eliminación de archivos temporales',
            'Creación Punto de Restauración',
            'Verificar espacio en disco',
            'Desactivar software no autorizado',
            'Analizar disco duro',
            'El Usuario de Windows tiene contraseña',
        ]
        
        sw_table_data = [['Actividad', 'SI', 'N.A./NO']]
        
        for activity in software_activities:
            activity_key = activity.lower().replace(' ', '_')
            status = activities_data.get(f'software_{activity_key}', '')
            sw_table_data.append([
                activity,
                '☑' if status == 'SI' else '☐',
                '☑' if status in ['N.A.', 'NO'] else '☐'
            ])
        
        sw_table = Table(sw_table_data, colWidths=[12*cm, 2*cm, 2*cm])
        sw_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d0e0f0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(sw_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Observations Section
        story.append(Paragraph("📝 OBSERVACIONES GENERALES", self.styles['SectionHeader']))
        obs_gen = Paragraph(maintenance.observaciones_generales or '_' * 80, self.styles['Normal'])
        story.append(obs_gen)
        story.append(Spacer(1, 0.3*cm))
        
        story.append(Paragraph("🔒 OBSERVACIONES SEGURIDAD DE LA INFORMACIÓN", self.styles['SectionHeader']))
        obs_seg = Paragraph(maintenance.observaciones_seguridad or '_' * 80, self.styles['Normal'])
        story.append(obs_seg)
        story.append(Spacer(1, 0.5*cm))
        
        # Signatures Section
        sig_data = [
            ['Responsable de Mantenimiento', 'Usuario del Equipo'],
            ['Firma: ___________________', 'Firma: ___________________'],
            [f'Nombre: {maintenance.performed_by}', 'Nombre: ___________________'],
            ['Cargo: ___________________', 'Cédula: ___________________'],
        ]
        
        sig_table = Table(sig_data, colWidths=[8*cm, 8*cm])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(sig_table)
        
        # Add signature images if available
        if hasattr(maintenance, 'signature') and maintenance.signature:
            story.append(Spacer(1, 0.2*cm))
            try:
                sig_img = RLImage(maintenance.signature.image.path, width=3*cm, height=1.5*cm)
                story.append(sig_img)
            except:
                pass
        
        if hasattr(maintenance, 'second_signature') and maintenance.second_signature:
            story.append(Spacer(1, 0.2*cm))
            try:
                sig2_img = RLImage(maintenance.second_signature.image.path, width=3*cm, height=1.5*cm)
                story.append(sig2_img)
            except:
                pass
        
        story.append(Spacer(1, 0.5*cm))
        
        # Service Rating
        rating_options = ['Excelente', 'Bueno', 'Regular', 'Malo']
        rating_row = ['Cómo califica el servicio:']
        for option in rating_options:
            checked = '☑' if maintenance.calificacion_servicio == option.lower() else '☐'
            rating_row.append(f'{checked} {option}')
        
        rating_table = Table([rating_row], colWidths=[5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        rating_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(rating_table)
        story.append(Spacer(1, 0.3*cm))
        
        story.append(Paragraph("<b>Observaciones del usuario:</b>", self.styles['Normal']))
        user_obs = Paragraph(maintenance.observaciones_usuario or '_' * 80, self.styles['Normal'])
        story.append(user_obs)
        
        # Add photos section if available
        if maintenance.photos.exists():
            story.append(PageBreak())
            story.append(Paragraph("📷 FOTOGRAFÍAS DEL MANTENIMIENTO", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.3*cm))
            
            for idx, photo in enumerate(maintenance.photos.all(), 1):
                try:
                    img = RLImage(photo.image.path, width=8*cm, height=6*cm)
                    story.append(Paragraph(f"Foto {idx}:", self.styles['FieldLabel']))
                    story.append(img)
                    story.append(Spacer(1, 0.3*cm))
                except Exception as e:
                    story.append(Paragraph(f"Error cargando foto {idx}: {str(e)}", self.styles['Normal']))
        
        # Build PDF with custom header/footer
        header_footer = PDFHeaderFooter(header_config)
        doc.build(story, onFirstPage=header_footer.draw_header, onLaterPages=header_footer.draw_header)
        
        buffer.seek(0)
        return buffer


    def _generate_printer_scanner_report(self, maintenance: Maintenance) -> BytesIO:
        """Generate Formato 2: Rutina de Mantenimiento Preventivo para Impresoras y Escáner."""
        buffer = BytesIO()
        
        # Configure header
        header_config = {
            'organization': 'ALCALDÍA DE PASTO',
            'department': 'GESTIÓN DE TECNOLOGÍAS DE LA INFORMACIÓN',
            'codigo': 'GTI-F-016',
            'version': '02',
            'vigencia': '18-Jul-19',
            **self.header_config
        }
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=3.5*cm,
            bottomMargin=2*cm,
            leftMargin=2*cm,
            rightMargin=2*cm
        )
        
        story = []
        
        # Title
        title = Paragraph(
            "🖨 FORMATO 2: RUTINA DE MANTENIMIENTO PREVENTIVO PARA IMPRESORAS Y ESCÁNER",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.3*cm))
        
        # Basic Information
        basic_info_data = [
            ['Sede:', maintenance.sede or '_' * 40],
            ['Dependencia:', maintenance.dependencia or '_' * 40],
            ['Oficina:', maintenance.oficina or '_' * 40],
            ['Placa:', maintenance.placa or maintenance.equipment.code],
            ['Fecha Mantenimiento:', maintenance.maintenance_date.strftime('%d/%m/%Y')],
        ]
        
        time_data = [
            ['Hora Inicio:', maintenance.hora_inicio.strftime('%H:%M') if maintenance.hora_inicio else '_______',
             'Hora Final:', maintenance.hora_final.strftime('%H:%M') if maintenance.hora_final else '_______']
        ]
        
        activities_data = maintenance.activities or {}
        brand_model = [
            ['Marca y Modelo Impresora:', activities_data.get('marca_modelo_impresora', '_' * 40)],
            ['Marca y Modelo Escáner:', activities_data.get('marca_modelo_escaner', '_' * 40)],
        ]
        
        for row in basic_info_data:
            table = Table([row], colWidths=[5*cm, 12*cm])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(table)
        
        time_table = Table([time_data[0]], colWidths=[2.5*cm, 3*cm, 2.5*cm, 3*cm])
        time_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(time_table)
        
        for row in brand_model:
            table = Table([row], colWidths=[5*cm, 12*cm])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(table)
        
        story.append(Spacer(1, 0.5*cm))
        
        # Scanner Section
        story.append(Paragraph("📠 RUTINA DE ESCÁNER", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*cm))
        
        scanner_activities = [
            'Limpieza general',
            'Alineación de papel',
            'Configuración del equipo',
            'Pruebas de funcionamiento',
        ]
        
        scanner_table_data = [['Actividad', 'SI', 'N.A.']]
        
        for activity in scanner_activities:
            activity_key = activity.lower().replace(' ', '_')
            status = activities_data.get(f'scanner_{activity_key}', '')
            scanner_table_data.append([
                activity,
                '☑' if status == 'SI' else '☐',
                '☑' if status == 'N.A.' else '☐'
            ])
        
        scanner_table = Table(scanner_table_data, colWidths=[12*cm, 2*cm, 2*cm])
        scanner_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d0e0f0')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(scanner_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Printer Section
        story.append(Paragraph("🖨 RUTINA DE IMPRESORAS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*cm))
        
        printer_activities = [
            'Limpieza de carcaza',
            'Limpieza tóner',
            'Limpieza tarjeta lógica',
            'Limpieza de sensores',
            'Limpieza de rodillo',
            'Limpieza de correas dentadas o guías',
            'Limpieza de ventiladores',
            'Limpieza de cabezal impresora matriz de punto e inyección tinta',
            'Limpieza de engranaje',
            'Limpieza de fusor',
            'Limpieza tarjeta de poder',
            'Alineación de rodillos alimentación de papel',
            'Configuración del equipo',
            'Pruebas de funcionamiento',
        ]
        
        printer_table_data = [['Actividad', 'SI', 'N.A.']]
        
        for activity in printer_activities:
            activity_key = activity.lower().replace(' ', '_')
            status = activities_data.get(f'printer_{activity_key}', '')
            printer_table_data.append([
                activity,
                '☑' if status == 'SI' else '☐',
                '☑' if status == 'N.A.' else '☐'
            ])
        
        printer_table = Table(printer_table_data, colWidths=[12*cm, 2*cm, 2*cm])
        printer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d0e0f0')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(printer_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Diagnosis and Observations
        story.append(Paragraph("🔍 DIAGNÓSTICO", self.styles['SectionHeader']))
        diagnosis = Paragraph(maintenance.description or '_' * 80, self.styles['Normal'])
        story.append(diagnosis)
        story.append(Spacer(1, 0.3*cm))
        
        story.append(Paragraph("🗒 OBSERVACIONES ADICIONALES", self.styles['SectionHeader']))
        obs = Paragraph(maintenance.observaciones_generales or '_' * 80, self.styles['Normal'])
        story.append(obs)
        story.append(Spacer(1, 0.5*cm))
        
        # Signatures
        sig_data = [
            ['Responsable de Mantenimiento', 'Responsable del Equipo'],
            ['Firma: ___________________', 'Firma: ___________________'],
            [f'Nombre: {maintenance.performed_by}', 'Nombre: ___________________'],
            ['Cargo: ___________________', 'Cargo: ___________________'],
        ]
        
        sig_table = Table(sig_data, colWidths=[8*cm, 8*cm])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(sig_table)
        
        # Add signature images if available
        if hasattr(maintenance, 'signature') and maintenance.signature:
            story.append(Spacer(1, 0.2*cm))
            try:
                sig_img = RLImage(maintenance.signature.image.path, width=3*cm, height=1.5*cm)
                story.append(sig_img)
            except:
                pass
        
        # Add photos section if available
        if maintenance.photos.exists():
            story.append(PageBreak())
            story.append(Paragraph("📷 FOTOGRAFÍAS DEL MANTENIMIENTO", self.styles['SectionHeader']))
            story.append(Spacer(1, 0.3*cm))
            
            for idx, photo in enumerate(maintenance.photos.all(), 1):
                try:
                    img = RLImage(photo.image.path, width=8*cm, height=6*cm)
                    story.append(Paragraph(f"Foto {idx}:", self.styles['FieldLabel']))
                    story.append(img)
                    story.append(Spacer(1, 0.3*cm))
                except Exception as e:
                    story.append(Paragraph(f"Error cargando foto {idx}: {str(e)}", self.styles['Normal']))
        
        # Build PDF
        header_footer = PDFHeaderFooter(header_config)
        doc.build(story, onFirstPage=header_footer.draw_header, onLaterPages=header_footer.draw_header)
        
        buffer.seek(0)
        return buffer
    
    def _generate_generic_report(self, maintenance: Maintenance) -> BytesIO:
        """Generate a generic maintenance report."""
        buffer = BytesIO()
        
        header_config = {
            'organization': 'ALCALDÍA DE PASTO',
            'department': 'GESTIÓN DE TECNOLOGÍAS DE LA INFORMACIÓN',
            'codigo': 'GTI-F-000',
            'version': '01',
            'vigencia': datetime.now().strftime('%d-%b-%y'),
            **self.header_config
        }
        
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=3.5*cm, bottomMargin=2*cm)
        story = []
        
        title = Paragraph(f"Reporte de Mantenimiento - {maintenance.equipment.code}", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5*cm))
        
        # Basic info
        info_data = [
            ['Equipo:', maintenance.equipment.name],
            ['Código:', maintenance.equipment.code],
            ['Ubicación:', maintenance.equipment.location or 'N/A'],
            ['Fecha:', maintenance.maintenance_date.strftime('%d/%m/%Y')],
            ['Realizado por:', maintenance.performed_by],
            ['Descripción:', maintenance.description],
        ]
        
        for row in info_data:
            table = Table([row], colWidths=[5*cm, 12*cm])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(table)
        
        # Build PDF
        header_footer = PDFHeaderFooter(header_config)
        doc.build(story, onFirstPage=header_footer.draw_header, onLaterPages=header_footer.draw_header)
        
        buffer.seek(0)
        return buffer


class WeasyPrintGenerator(ReportGenerator):
    """PDF generator using WeasyPrint - deprecated, use ReportLabGenerator instead."""

    def generate(self, maintenance: Maintenance) -> BytesIO:
        # Fallback to ReportLab
        fallback = ReportLabGenerator()
        return fallback.generate(maintenance)
        
        # html_content = f"""
        # <html>
        # <head>
        #     <style>
        #         body {{ font-family: Arial, sans-serif; margin: 40px; }}
        #         .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        #         .photo {{ margin: 10px 0; max-width: 300px; }}
        #         .signature {{ margin: 20px 0; max-width: 200px; }}
        #     </style>
        # </head>
        # <body>
        #     <div class="header">
        #         <h1>Maintenance Report - {maintenance.equipment.code}</h1>
        #         <p><strong>Equipment:</strong> {maintenance.equipment.name}</p>
        #         <p><strong>Location:</strong> {maintenance.equipment.location or 'N/A'}</p>
        #         <p><strong>Date:</strong> {maintenance.maintenance_date}</p>
        #         <p><strong>Performed by:</strong> {maintenance.performed_by}</p>
        #         <p><strong>Description:</strong> {maintenance.description}</p>
        #     </div>

        #     <h2>Photos</h2>
        # """

        # # Add photos
        # if maintenance.photos.exists():
        #     for photo in maintenance.photos.all():
        #         try:
        #             photo_url = settings.MEDIA_URL + str(photo.image)
        #             html_content += f'<img src="{photo_url}" class="photo" alt="Maintenance photo"><br/>'
        #         except Exception as e:
        #             html_content += f'<p>Error loading photo: {str(e)}</p>'

        # # Add signature
        # if hasattr(maintenance, 'signature') and maintenance.signature:
        #     try:
        #         sig_url = settings.MEDIA_URL + str(maintenance.signature.image)
        #         html_content += f'<h2>Signature</h2><img src="{sig_url}" class="signature" alt="Signature">'
        #     except Exception as e:
        #         html_content += f'<p>Error loading signature: {str(e)}</p>'

        # html_content += """
        # </body>
        # </html>
        # """

        # # Generate PDF
        # html_doc = HTML(string=html_content, base_url=settings.MEDIA_ROOT)
        # buffer = BytesIO()
        # html_doc.write_pdf(buffer)
        # buffer.seek(0)
        # return buffer


# Factory function to get the appropriate generator
def get_report_generator(generator_type: str = 'reportlab', header_config: dict = None) -> ReportGenerator:
    """
    Factory function to get report generator by type.
    
    Args:
        generator_type: Type of generator ('reportlab' recommended)
        header_config: Optional dictionary with header configuration:
            - organization: Organization name (default: 'ALCALDÍA DE PASTO')
            - department: Department name (default: 'GESTIÓN DE TECNOLOGÍAS DE LA INFORMACIÓN')
            - codigo: Form code (e.g., 'GTI-F-015')
            - version: Version number (e.g., '03')
            - vigencia: Validity date (e.g., '18-Jul-19')
            - logo_path: Path to organization logo
    
    Returns:
        ReportGenerator instance
        
    Example:
        >>> config = {
        ...     'codigo': 'GTI-F-015',
        ...     'version': '03',
        ...     'vigencia': '18-Jul-19'
        ... }
        >>> generator = get_report_generator('reportlab', config)
        >>> pdf_buffer = generator.generate(maintenance_instance)
    """
    if generator_type.lower() == 'reportlab':
        return ReportLabGenerator(header_config=header_config)
    elif generator_type.lower() == 'weasyprint':
        return ReportLabGenerator(header_config=header_config)  # Fallback to ReportLab
    else:
        raise ValueError(f"Unknown generator type: {generator_type}")


# Documentation and implementation notes
IMPLEMENTATION_NOTES = """
PDF Generation Implementation - ReportLab

This module implements PDF generation for maintenance reports using ReportLab library.

FEATURES:
---------
1. Parameterizable Headers:
   - Organization name
   - Department name
   - Form code (e.g., GTI-F-015)
   - Version and validity date
   - Optional logo support

2. Two Main Formats:
   - Formato 1: Computer Equipment Maintenance (GTI-F-015)
   - Formato 2: Printer and Scanner Maintenance (GTI-F-016)

3. Dynamic Content:
   - Checklist tables with SI/N.A./NO options
   - Signature fields with image support
   - Photo attachments
   - Service rating
   - Custom observations

4. Professional Styling:
   - Custom color schemes
   - Proper spacing and alignment
   - Grid-based layouts
   - Unicode emoji support

USAGE:
------
1. Basic usage:
   ```python
   from api.reports import get_report_generator
   
   generator = get_report_generator('reportlab')
   pdf_buffer = generator.generate(maintenance)
   ```

2. With custom header:
   ```python
   header_config = {
       'codigo': 'GTI-F-015',
       'version': '04',
       'vigencia': '15-Nov-25',
       'logo_path': '/path/to/logo.png'
   }
   generator = get_report_generator('reportlab', header_config)
   pdf_buffer = generator.generate(maintenance)
   ```

3. Saving to file:
   ```python
   with open('report.pdf', 'wb') as f:
       f.write(pdf_buffer.getvalue())
   ```

MAINTENANCE MODEL REQUIREMENTS:
-------------------------------
The Maintenance model should have these fields for optimal PDF generation:
- maintenance_type: 'computer' or 'printer_scanner'
- sede, dependencia, oficina, placa
- maintenance_date, hora_inicio, hora_final
- performed_by
- activities: JSONField with activity statuses
- observaciones_generales, observaciones_seguridad
- calificacion_servicio, observaciones_usuario
- Relationships: photos, signature, second_signature

ACTIVITIES JSON FORMAT:
-----------------------
For computer maintenance:
{
    "hardware_limpieza_interna_de_la_torre": "SI",
    "hardware_limpieza_del_teclado": "N.A.",
    "software_crear_partición_de_datos": "SI",
    ...
}

For printer/scanner maintenance:
{
    "scanner_limpieza_general": "SI",
    "printer_limpieza_de_carcaza": "SI",
    "marca_modelo_impresora": "HP LaserJet Pro M404n",
    "marca_modelo_escaner": "Epson DS-530",
    ...
}

LIBRARY COMPARISON:
-------------------
ReportLab (Current Implementation):
✓ Pure Python, no external dependencies
✓ Excellent performance and low memory usage
✓ Precise layout control
✓ Good for structured forms and tables
✓ Extensive documentation
✓ Active maintenance
- Steeper learning curve for complex layouts

xhtml2pdf (Previously used):
- HTML/CSS to PDF conversion
- Limited CSS support
- Performance issues with large files
- Deprecated in favor of ReportLab

WeasyPrint:
+ Better HTML/CSS support
- Requires external dependencies (GTK, Cairo)
- Installation challenges on Windows
- Not suitable for this project

RECOMMENDATION: ReportLab is the best choice for this project due to:
- No external dependencies
- Better control over table layouts
- Excellent performance
- Easy to maintain
"""
