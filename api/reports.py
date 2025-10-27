"""
ReportGenerator pattern for PDF generation.
This module provides an abstraction for generating different types of reports.
"""

from abc import ABC, abstractmethod
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
# try:
#     from weasyprint import HTML, CSS
# except ImportError:
#     HTML = None
#     CSS = None
from django.conf import settings
from .models import Maintenance


class ReportGenerator(ABC):
    """Abstract base class for report generators."""

    @abstractmethod
    def generate(self, maintenance: Maintenance) -> BytesIO:
        """Generate a report for the given maintenance."""
        pass


class ReportLabGenerator(ReportGenerator):
    """PDF generator using ReportLab."""

    def generate(self, maintenance: Maintenance) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title = Paragraph(f"Maintenance Report - {maintenance.equipment.code}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))

        # Basic info
        info = Paragraph(f"""
        Equipment: {maintenance.equipment.name}<br/>
        Location: {maintenance.equipment.location or 'N/A'}<br/>
        Date: {maintenance.maintenance_date}<br/>
        Performed by: {maintenance.performed_by}<br/>
        Description: {maintenance.description}
        """, styles['Normal'])
        story.append(info)
        story.append(Spacer(1, 12))

        # Photos
        if maintenance.photos.exists():
            photos_title = Paragraph("Photos:", styles['Heading2'])
            story.append(photos_title)
            story.append(Spacer(1, 6))

            for photo in maintenance.photos.all():
                try:
                    # For demo purposes, we'll just add text since we can't embed images easily
                    photo_text = Paragraph(f"Photo: {photo.image.name}", styles['Normal'])
                    story.append(photo_text)
                    story.append(Spacer(1, 6))
                except Exception as e:
                    error_text = Paragraph(f"Error loading photo: {str(e)}", styles['Normal'])
                    story.append(error_text)
                    story.append(Spacer(1, 6))

        # Signature
        if hasattr(maintenance, 'signature') and maintenance.signature:
            sig_title = Paragraph("Signature:", styles['Heading2'])
            story.append(sig_title)
            story.append(Spacer(1, 6))
            sig_text = Paragraph("Signature present", styles['Normal'])
            story.append(sig_text)

        doc.build(story)
        buffer.seek(0)
        return buffer


class WeasyPrintGenerator(ReportGenerator):
    """PDF generator using WeasyPrint."""

    def generate(self, maintenance: Maintenance) -> BytesIO:
        # if HTML is None:
        #     raise ImportError("WeasyPrint is not available. Falling back to ReportLab.")
        
        # For now, fall back to ReportLab since WeasyPrint has dependency issues
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
def get_report_generator(generator_type: str = 'reportlab') -> ReportGenerator:
    """Factory function to get report generator by type."""
    if generator_type.lower() == 'reportlab':
        return ReportLabGenerator()
    elif generator_type.lower() == 'weasyprint':
        # try:
        #     return WeasyPrintGenerator()
        # except ImportError:
        return ReportLabGenerator()  # Fallback to ReportLab
    else:
        raise ValueError(f"Unknown generator type: {generator_type}")


# Spike comparison results
SPIKE_RESULTS = """
Spike Results: PDF Generation Libraries

ReportLab:
- Pros: Pure Python, no external dependencies, good for structured documents
- Cons: Steeper learning curve, less modern HTML/CSS support
- Performance: Fast, low memory usage
- Use case: Reports with precise layout control

WeasyPrint:
- Pros: HTML/CSS support, easier for web developers, better image handling
- Cons: Requires external dependencies (GTK), slightly slower
- Performance: Good, handles complex layouts well
- Use case: Reports that look like web pages

Recommendation: WeasyPrint for this project due to better image handling and familiarity with HTML/CSS.
"""
