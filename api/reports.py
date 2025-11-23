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
from reportlab.platypus import (
    SimpleDocTemplate, 
    Table, 
    TableStyle, 
    Paragraph, 
    Spacer, 
    Image as RLImage,  # Renombrar para evitar conflictos
    PageBreak,
    Flowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import os
from django.conf import settings

# Importar modelos
from .models import Maintenance, Incident, Equipment


class MaintenanceReportPDF:
    """Generate PDF report for maintenance with parametrized headers"""
    
    def __init__(self, maintenance: Maintenance):
        self.maintenance = maintenance
        self.buffer = BytesIO()
        self.width, self.height = A4
        
    def _header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 8)
        
        # Logo (if exists)
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            canvas.drawImage(logo_path, 30, self.height - 50, width=60, height=40, preserveAspectRatio=True)
        
        # Header table
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(100, self.height - 30, "ALCALDÍA MUNICIPAL")
        canvas.setFont('Helvetica', 8)
        canvas.drawString(100, self.height - 42, "Sistema de Gestión de Mantenimiento")
        
        # Document info box (right side)
        canvas.setFont('Helvetica-Bold', 7)
        canvas.drawString(self.width - 150, self.height - 25, "Código: GTI-F-015")
        canvas.drawString(self.width - 150, self.height - 35, "Versión: 01")
        canvas.drawString(self.width - 150, self.height - 45, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
        
        # Header line
        canvas.setStrokeColor(colors.HexColor('#003366'))
        canvas.setLineWidth(2)
        canvas.line(30, self.height - 60, self.width - 30, self.height - 60)
        
        # Footer
        canvas.setFont('Helvetica', 7)
        canvas.drawString(30, 30, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        canvas.drawString(self.width - 150, 30, f"Página {doc.page}")
        
        # Footer line
        canvas.setStrokeColor(colors.HexColor('#003366'))
        canvas.setLineWidth(1)
        canvas.line(30, 40, self.width - 30, 40)
        
        canvas.restoreState()

    def generate(self) -> BytesIO:
        """Generate the PDF report"""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=80,
            bottomMargin=60,
        )
        
        # Container for elements
        elements: list[Flowable] = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#003366'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_JUSTIFY
        )
        
        # Title
        title = Paragraph("REPORTE DE MANTENIMIENTO", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Equipment Information Section
        equipment_heading = Paragraph("1. INFORMACIÓN DEL EQUIPO", heading_style)
        elements.append(equipment_heading)
        
        equipment = self.maintenance.equipment
        equipment_data = [
            ['Placa:', self.maintenance.placa or equipment.code or equipment.serial_number or 'N/A', 'Tipo:', equipment.name],
            ['Marca:', equipment.brand or 'N/A', 'Modelo:', equipment.model or 'N/A'],
            ['Serial:', equipment.serial_number or 'N/A', 'Ubicación:', equipment.location or self.maintenance.ubicacion or 'N/A'],
            ['Dependencia:', self.maintenance.dependencia or equipment.dependencia or 'N/A', 'Sede:', self.maintenance.sede or 'N/A'],
            ['Oficina:', self.maintenance.oficina or 'N/A', '', ''],
        ]
        
        equipment_table = Table(equipment_data, colWidths=[2*cm, 6*cm, 2*cm, 6*cm])
        equipment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#003366')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#003366')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(equipment_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Maintenance Information Section
        maintenance_heading = Paragraph("2. INFORMACIÓN DEL MANTENIMIENTO", heading_style)
        elements.append(maintenance_heading)
        
        maintenance_date = self.maintenance.scheduled_date or self.maintenance.completion_date or datetime.now()
        maintenance_data = [
            ['Tipo:', self.maintenance.get_maintenance_type_display() if hasattr(self.maintenance, 'get_maintenance_type_display') else self.maintenance.maintenance_type or 'N/A', 'Fecha:', maintenance_date.strftime('%d/%m/%Y')],
            ['Hora Inicio:', str(self.maintenance.hora_inicio) if self.maintenance.hora_inicio else 'N/A', 'Hora Final:', str(self.maintenance.hora_final) if self.maintenance.hora_final else 'N/A'],
            ['Técnico:', self.maintenance.technician.get_full_name() if self.maintenance.technician else 'N/A', 
             'Estado:', self.maintenance.get_status_display() if hasattr(self.maintenance, 'get_status_display') else self.maintenance.status or 'N/A'],
        ]
        
        if self.maintenance.cost:
            maintenance_data.append(['Costo:', f"${self.maintenance.cost:,.2f}", '', ''])
        
        if self.maintenance.calificacion_servicio:
            maintenance_data.append(['Calificación:', f"{self.maintenance.calificacion_servicio}/5", '', ''])
        
        maintenance_table = Table(maintenance_data, colWidths=[2*cm, 6*cm, 2.5*cm, 5.5*cm])
        maintenance_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#003366')),
            ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#003366')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(maintenance_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Work Description Section
        description_heading = Paragraph("3. DESCRIPCIÓN DEL TRABAJO REALIZADO", heading_style)
        elements.append(description_heading)
        
        description_text = Paragraph(self.maintenance.description or 'Sin descripción', normal_style)
        elements.append(description_text)
        elements.append(Spacer(1, 0.2*inch))
        
        # Activities Section
        if self.maintenance.activities:
            activities_heading = Paragraph("4. ACTIVIDADES REALIZADAS", heading_style)
            elements.append(activities_heading)
            
            # Si activities es un dict/JSON, formatearlo
            activities_text = str(self.maintenance.activities) if self.maintenance.activities else 'No se registraron actividades'
            activities_para = Paragraph(activities_text, normal_style)
            elements.append(activities_para)
            elements.append(Spacer(1, 0.2*inch))
        
        # Observations Section
        section_num = 5
        if self.maintenance.observaciones_generales:
            obs_heading = Paragraph(f"{section_num}. OBSERVACIONES GENERALES", heading_style)
            elements.append(obs_heading)
            obs_text = Paragraph(self.maintenance.observaciones_generales, normal_style)
            elements.append(obs_text)
            elements.append(Spacer(1, 0.2*inch))
            section_num += 1
        
        if self.maintenance.observaciones_seguridad:
            seg_heading = Paragraph(f"{section_num}. OBSERVACIONES DE SEGURIDAD", heading_style)
            elements.append(seg_heading)
            seg_text = Paragraph(self.maintenance.observaciones_seguridad, normal_style)
            elements.append(seg_text)
            elements.append(Spacer(1, 0.2*inch))
            section_num += 1
        
        if self.maintenance.observaciones_usuario:
            user_heading = Paragraph(f"{section_num}. OBSERVACIONES DEL USUARIO", heading_style)
            elements.append(user_heading)
            user_text = Paragraph(self.maintenance.observaciones_usuario, normal_style)
            elements.append(user_text)
            elements.append(Spacer(1, 0.2*inch))
            section_num += 1
        
        # Photos Section
        photos = self.maintenance.photos.all()
        if photos:
            photos_heading = Paragraph(f"{section_num}. EVIDENCIA FOTOGRÁFICA", heading_style)
            elements.append(photos_heading)
            section_num += 1
            
            photo_data = []
            photo_row = []
            for idx, photo in enumerate(photos):
                if photo.photo:
                    try:
                        # Intentar obtener la ruta del archivo
                        photo_path = photo.photo.path if hasattr(photo.photo, 'path') else None
                        if photo_path and os.path.exists(photo_path):
                            img = RLImage(photo_path, width=2.5*inch, height=2*inch)
                            photo_row.append(img)
                            
                            if len(photo_row) == 2 or idx == len(photos) - 1:
                                photo_data.append(photo_row)
                                photo_row = []
                    except Exception as e:
                        print(f"Error loading image: {e}")
            
            if photo_data:
                photo_table = Table(photo_data, colWidths=[3*inch, 3*inch])
                photo_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ]))
                elements.append(photo_table)
                elements.append(Spacer(1, 0.3*inch))
        
        # Signatures Section
        elements.append(Spacer(1, 0.5*inch))
        signatures_heading = Paragraph(f"{section_num}. FIRMAS", heading_style)
        elements.append(signatures_heading)
        
        # Obtener firmas del mantenimiento
        signatures = self.maintenance.signatures.all()
        second_signatures = self.maintenance.second_signatures.all()
        
        signature_data = []
        signature_images = []
        
        # Primera firma (técnico)
        if signatures:
            sig = signatures.first()
            if sig.signature_image:
                try:
                    sig_path = sig.signature_image.path if hasattr(sig.signature_image, 'path') else None
                    if sig_path and os.path.exists(sig_path):
                        sig_img = RLImage(sig_path, width=2*inch, height=1*inch)
                        signature_images.append(sig_img)
                    else:
                        signature_images.append('')
                except:
                    signature_images.append('')
            else:
                signature_images.append('')
        else:
            signature_images.append('')
        
        # Segunda firma (usuario/supervisor)
        if second_signatures:
            sig2 = second_signatures.first()
            if sig2.signature_image:
                try:
                    sig2_path = sig2.signature_image.path if hasattr(sig2.signature_image, 'path') else None
                    if sig2_path and os.path.exists(sig2_path):
                        sig2_img = RLImage(sig2_path, width=2*inch, height=1*inch)
                        signature_images.append(sig2_img)
                    else:
                        signature_images.append('')
                except:
                    signature_images.append('')
            else:
                signature_images.append('')
        else:
            signature_images.append('')
        
        signature_data.append(signature_images)
        signature_data.append(['_' * 40, '_' * 40])
        
        # Nombres
        tech_name = signatures.first().signer_name if signatures else (
            self.maintenance.technician.get_full_name() if self.maintenance.technician else 
            self.maintenance.performed_by or 'Técnico'
        )
        user_name = second_signatures.first().signer_name if second_signatures else 'Usuario/Supervisor'
        
        signature_data.append(['Técnico Responsable', 'Usuario/Supervisor'])
        signature_data.append([tech_name, user_name])
        
        signature_table = Table(signature_data, colWidths=[3.5*inch, 3.5*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(signature_table)
        
        # Build PDF
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        
        self.buffer.seek(0)
        return self.buffer


class IncidentReportPDF:
    """Generate PDF report for incidents"""
    
    def __init__(self, incident: Incident):
        self.incident = incident
        self.buffer = BytesIO()
        self.width, self.height = A4
    
    def _header_footer(self, canvas, doc):
        """Add header and footer"""
        canvas.saveState()
        
        canvas.setFont('Helvetica-Bold', 10)
        canvas.drawString(100, self.height - 30, "REPORTE DE INCIDENTE")
        canvas.setFont('Helvetica', 7)
        canvas.drawString(30, 30, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        canvas.restoreState()
    
    def generate(self) -> BytesIO:
        """Generate incident PDF report"""
        doc = SimpleDocTemplate(self.buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=80, bottomMargin=60)
        elements: list[Flowable] = []
        styles = getSampleStyleSheet()
        
        # Title
        title = Paragraph(f"REPORTE DE INCIDENTE #{self.incident.id}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Incident data
        data = [
            ['Equipo:', self.incident.equipo.placa, 'Tipo:', self.incident.get_tipo_incidente_display()],
            ['Estado:', self.incident.get_estado_display(), 'Prioridad:', self.incident.get_prioridad_display()],
            ['Fecha Reporte:', self.incident.fecha_reporte.strftime('%d/%m/%Y %H:%M'), 
             'Reportado por:', self.incident.reportado_por.get_full_name() if self.incident.reportado_por else 'N/A'],
        ]
        
        table = Table(data, colWidths=[2*cm, 6*cm, 2*cm, 6*cm])
        table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Description
        desc_heading = Paragraph("Descripción:", styles['Heading2'])
        elements.append(desc_heading)
        desc = Paragraph(self.incident.descripcion, styles['Normal'])
        elements.append(desc)
        
        if self.incident.solucion:
            elements.append(Spacer(1, 0.2*inch))
            sol_heading = Paragraph("Solución:", styles['Heading2'])
            elements.append(sol_heading)
            sol = Paragraph(self.incident.solucion, styles['Normal'])
            elements.append(sol)
        
        doc.build(elements, onFirstPage=self._header_footer, onLaterPages=self._header_footer)
        self.buffer.seek(0)
        return self.buffer


class BatchMaintenanceReportPDF:
    """Generate batch PDF reports for multiple maintenances"""
    
    def __init__(self, maintenances: list[Maintenance]):
        self.maintenances = maintenances
        self.buffer = BytesIO()
    
    def generate(self) -> BytesIO:
        """Generate batch PDF report"""
        doc = SimpleDocTemplate(self.buffer, pagesize=A4)
        elements: list[Flowable] = []
        styles = getSampleStyleSheet()
        
        # Cover page
        cover_title = Paragraph(
            f"REPORTES DE MANTENIMIENTO<br/>{len(self.maintenances)} Registros",
            styles['Title']
        )
        elements.append(cover_title)
        elements.append(Spacer(1, 0.5*inch))
        
        cover_date = Paragraph(
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles['Normal']
        )
        elements.append(cover_date)
        elements.append(PageBreak())
        
        # Add each maintenance report
        for idx, maintenance in enumerate(self.maintenances):
            report_gen = MaintenanceReportPDF(maintenance)
            # Note: This is simplified - in production you'd merge the PDFs properly
            
            heading = Paragraph(
                f"Reporte {idx + 1}: {maintenance.equipo.placa}",
                styles['Heading1']
            )
            elements.append(heading)
            elements.append(Spacer(1, 0.2*inch))
            
            if idx < len(self.maintenances) - 1:
                elements.append(PageBreak())
        
        doc.build(elements)
        self.buffer.seek(0)
        return self.buffer


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


# Factory function para obtener el generador de reportes
def get_report_generator(report_type='reportlab', config=None):
    """
    Factory function para obtener un generador de reportes.
    
    Args:
        report_type: Tipo de generador ('reportlab', 'weasyprint', etc.)
        config: Configuración opcional para el generador
    
    Returns:
        Una instancia del generador de reportes
    """
    if report_type == 'reportlab':
        return ReportLabGenerator(config)
    else:
        raise ValueError(f"Tipo de reporte no soportado: {report_type}")


class ReportLabGenerator:
    """Generador de reportes usando ReportLab"""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def generate(self, maintenance):
        """
        Genera un PDF para un mantenimiento.
        
        Args:
            maintenance: Instancia de Maintenance
            
        Returns:
            BytesIO buffer con el PDF generado
        """
        report_pdf = MaintenanceReportPDF(maintenance)
        return report_pdf.generate()

