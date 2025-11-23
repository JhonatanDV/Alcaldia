from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


class ImageGenerator:
    def generate(self, data: dict) -> BytesIO:
        img = Image.new('RGB', (800, 1000), color='white')
        draw = ImageDraw.Draw(img)

        try:
            font_title = ImageFont.truetype('arial.ttf', 24)
            font_normal = ImageFont.truetype('arial.ttf', 14)
        except Exception:
            font_title = ImageFont.load_default()
            font_normal = ImageFont.load_default()

        draw.text((20, 20), 'REPORTE DE MANTENIMIENTO', fill='black', font=font_title)

        y = 80
        lines = [
            f"Código: {data.get('codigo','')}",
            f"Equipo: {data.get('equipment_name','')}",
            f"Tipo: {data.get('maintenance_type','')}",
            f"Estado: {data.get('status','')}",
            f"Fecha: {data.get('scheduled_date','')}",
            f"Técnico: {data.get('technician_name','')}",
            f"Ubicación: {data.get('sede','')} - {data.get('dependencia','')}",
        ]

        for line in lines:
            draw.text((20, y), line, fill='black', font=font_normal)
            y += 30

        activities = data.get('activities', []) or []
        if activities:
            y += 20
            draw.text((20, y), f"Actividades: {len(activities)}", fill='blue', font=font_normal)

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
