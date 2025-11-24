from django.template import Template as DjangoTemplate, Context
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io
import textwrap
import re
from typing import Optional, List, Dict, Any


class ReportLabPDFGenerator:
    """Generador de PDF sencillo usando ReportLab como fallback cuando
    WeasyPrint no está disponible. Convierte el HTML renderizado a texto
    plano (bastante básico) y lo pinta en páginas A4.
    """

    @staticmethod
    def _html_to_text(html: str) -> str:
        # Simple eliminación de tags HTML (no perfecto, pero suficiente para fallback)
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        # Collapse multiple spaces/newlines
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def render_template(
        html_content: str,
        css_content: Optional[str] | None,
        data: Dict[str, Any],
        background_bytes: Optional[bytes] = None,
        overlays: Optional[List[Dict[str, Any]]] = None,
    ) -> io.BytesIO:
        # Renderizar con motor de templates de Django
        template = DjangoTemplate(html_content)
        context = Context(data)
        rendered = template.render(context)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Márgenes
        left_margin = 40
        top_margin = height - 40
        max_width = width - 2 * left_margin

        # Si hay background, dibujar la imagen en página(s)
        if background_bytes:
            try:
                img = ImageReader(io.BytesIO(background_bytes))
                # Ajustar imagen al tamaño de la página manteniendo proporción
                iw, ih = img.getSize()
                scale = min(width / iw, height / ih)
                draw_w = iw * scale
                draw_h = ih * scale
                x_off = (width - draw_w) / 2
                y_off = (height - draw_h) / 2

                # Dibujar imagen
                p.drawImage(img, x_off, y_off, draw_w, draw_h)

                # Dibujar overlays si hay
                if overlays:
                    for ov in overlays:
                        text = str(ov.get('text', ''))
                        x_pct = float(ov.get('x_pct', 0))
                        y_pct = float(ov.get('y_pct', 0))
                        font_size = int(ov.get('font_size', 12))
                        # Convertir pct a coordenadas: y_pct desde arriba
                        x = x_off + (x_pct / 100.0) * draw_w
                        y = y_off + draw_h - (y_pct / 100.0) * draw_h
                        p.setFont('Helvetica', font_size)
                        # drawString usa origen abajo-izquierda
                        p.drawString(x, y, text)

            except Exception:
                # Fallback simple: caer al modo texto
                text = ReportLabPDFGenerator._html_to_text(rendered)
                wrapper = textwrap.TextWrapper(width=100)
                lines = wrapper.wrap(text)
                y = height - 40
                line_height = 12
                for line in lines:
                    if y < 60:
                        p.showPage()
                        y = height - 40
                    p.drawString(40, y, line)
                    y -= line_height
        else:
            # No background: renderizar texto plano
            text = ReportLabPDFGenerator._html_to_text(rendered)
            wrapper = textwrap.TextWrapper(width=100)
            lines = wrapper.wrap(text)
            y = height - 40
            line_height = 12
            for line in lines:
                if y < 60:
                    p.showPage()
                    y = height - 40
                p.drawString(40, y, line)
                y -= line_height

        p.save()
        buffer.seek(0)
        return buffer
