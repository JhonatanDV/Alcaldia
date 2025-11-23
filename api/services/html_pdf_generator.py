from weasyprint import HTML, CSS
from django.template import Template as DjangoTemplate, Context
import io

class HTMLPDFGenerator:
    """Generador de PDFs desde plantillas HTML usando WeasyPrint"""

    @staticmethod
    def render_template(html_content: str, css_content: str | None, data: dict) -> io.BytesIO:
        # Renderizar con el motor de templates de Django
        template = DjangoTemplate(html_content)
        context = Context(data)
        rendered_html = template.render(context)

        html = HTML(string=rendered_html)
        stylesheets = [CSS(string=css_content)] if css_content else None

        pdf_file = io.BytesIO()
        html.write_pdf(pdf_file, stylesheets=stylesheets)
        pdf_file.seek(0)
        return pdf_file

    @staticmethod
    def get_default_css() -> str:
        return """
        @page {
            size: A4;
            margin: 2cm;
        }
        body { font-family: Arial, sans-serif; font-size: 12pt; line-height: 1.6; }
        .header { text-align: center; margin-bottom: 2cm; border-bottom: 2px solid #333; padding-bottom: 1cm; }
        .header h1 { margin: 0; font-size: 24pt; }
        .info-section { margin-bottom: 1cm; }
        .info-section label { font-weight: bold; display: inline-block; width: 150px; }
        table { width: 100%; border-collapse: collapse; margin: 1cm 0; }
        table th, table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        table th { background-color: #f2f2f2; font-weight: bold; }
        .footer { margin-top: 2cm; text-align: center; font-size: 10pt; color: #666; }
        .total { text-align: right; font-size: 14pt; font-weight: bold; margin-top: 1cm; }
        """
