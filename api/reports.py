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
        
        equipment_data = [
            ['Placa:', self.maintenance.equipo.placa, 'Tipo:', self.maintenance.equipo.tipo],
            ['Marca:', self.maintenance.equipo.marca, 'Modelo:', self.maintenance.equipo.modelo],
            ['Serial:', self.maintenance.equipo.serial or 'N/A', 'Estado:', self.maintenance.equipo.estado],
            ['Dependencia:', self.maintenance.equipo.dependencia, 'Sede:', self.maintenance.equipo.sede or 'N/A'],
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
        
        maintenance_data = [
            ['Tipo:', self.maintenance.get_tipo_mantenimiento_display(), 'Fecha:', self.maintenance.fecha_mantenimiento.strftime('%d/%m/%Y')],
            ['Técnico:', self.maintenance.tecnico_responsable.get_full_name() if self.maintenance.tecnico_responsable else 'N/A', 
             'Próximo Mtto:', self.maintenance.proximo_mantenimiento.strftime('%d/%m/%Y') if self.maintenance.proximo_mantenimiento else 'N/A'],
        ]
        
        if self.maintenance.costo:
            maintenance_data.append(['Costo:', f"${self.maintenance.costo:,.2f}", '', ''])
        
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
        
        description_text = Paragraph(self.maintenance.descripcion_trabajo, normal_style)
        elements.append(description_text)
        elements.append(Spacer(1, 0.2*inch))
        
        # Parts Used Section
        if self.maintenance.repuestos_utilizados:
            parts_heading = Paragraph("4. REPUESTOS UTILIZADOS", heading_style)
            elements.append(parts_heading)
            parts_text = Paragraph(self.maintenance.repuestos_utilizados, normal_style)
            elements.append(parts_text)
            elements.append(Spacer(1, 0.2*inch))
        
        # Observations Section
        if self.maintenance.observaciones:
            obs_heading = Paragraph("5. OBSERVACIONES", heading_style)
            elements.append(obs_heading)
            obs_text = Paragraph(self.maintenance.observaciones, normal_style)
            elements.append(obs_text)
            elements.append(Spacer(1, 0.2*inch))
        
        # Photos Section
        photos = self.maintenance.photos.all()
        if photos:
            photos_heading = Paragraph("6. EVIDENCIA FOTOGRÁFICA", heading_style)
            elements.append(photos_heading)
            
            photo_data = []
            photo_row = []
            for idx, photo in enumerate(photos):
                if photo.image and os.path.exists(photo.image.path):
                    try:
                        img = RLImage(photo.image.path, width=2.5*inch, height=2*inch)
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
        signatures_heading = Paragraph("7. FIRMAS", heading_style)
        elements.append(signatures_heading)
        
        signature_data = [
            ['', ''],
            ['_' * 40, '_' * 40],
            ['Técnico Responsable', 'Supervisor'],
            [self.maintenance.tecnico_responsable.get_full_name() if self.maintenance.tecnico_responsable else '', ''],
        ]
        
        signature_table = Table(signature_data, colWidths=[3.5*inch, 3.5*inch])
        signature_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, 0), 30),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 5),
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
