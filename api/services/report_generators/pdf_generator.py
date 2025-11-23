from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO
from django.conf import settings
import os


class PDFGenerator:
    def generate(self, data: dict, logo_path: str | None = None, primary_color: str | None = None) -> BytesIO:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        # Header: optional logo and title
        if not primary_color:
            primary_color = getattr(settings, 'REPORT_PRIMARY_COLOR', None)

        # If logo_path provided or configured, draw it at header using reportlab canvas later
        elements.append(Paragraph('<b>REPORTE DE MANTENIMIENTO</b>', styles['Title']))
        elements.append(Paragraph(f"Código: {data.get('codigo','')}", styles['Normal']))
        elements.append(Spacer(1, 12))

        basic_data = [
            ['Equipo:', data.get('equipment_name','')],
            ['Código Equipo:', data.get('equipment_code','')],
            ['Serial:', data.get('equipment_serial','')],
            ['Tipo:', data.get('maintenance_type','')],
            ['Estado:', data.get('status','')],
            ['Fecha Programada:', data.get('scheduled_date','')],
            ['Fecha Completado:', data.get('completion_date','')],
            ['Técnico:', data.get('technician_name','')],
            ['Ubicación:', f"{data.get('sede','')} - {data.get('dependencia','')}"],
        ]

        table = Table(basic_data, colWidths=[150, 350])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        activities = data.get('activities', []) or []
        if activities:
            elements.append(Paragraph('<b>Actividades Realizadas</b>', styles['Heading2']))
            elements.append(Spacer(1, 8))

            activity_data = [['#', 'Descripción', 'Estado']]
            for idx, act in enumerate(activities, 1):
                activity_data.append([
                    str(idx),
                    act.get('description', 'N/A') if isinstance(act, dict) else str(act),
                    act.get('status', 'N/A') if isinstance(act, dict) else ''
                ])

            act_table = Table(activity_data, colWidths=[30, 400, 70])
            act_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(act_table)
            elements.append(Spacer(1, 20))

        if data.get('observations'):
            elements.append(Paragraph('<b>Observaciones</b>', styles['Heading2']))
            elements.append(Paragraph(data.get('observations',''), styles['Normal']))

        elements.append(Spacer(1, 30))
        signature_data = [
            ['Elaborado:', data.get('elaborado_por',''), 'Revisado:', data.get('revisado_por','')],
            ['_________________', '', '_________________', ''],
        ]
        sig_table = Table(signature_data, colWidths=[100, 150, 100, 150])
        elements.append(sig_table)

        # If logo_path is provided, attempt to draw it by creating a custom onFirstPage
        def _on_first_page(canvas_obj, doc_obj):
            # Draw logo if exists
            lp = logo_path or getattr(settings, 'REPORT_LOGO_PATH', None)
            if lp:
                try:
                    if not os.path.isabs(lp):
                        # try relative to project base dir
                        base = getattr(settings, 'BASE_DIR', None)
                        if base:
                            candidate = os.path.join(base, lp)
                        else:
                            candidate = lp
                    else:
                        candidate = lp

                    if os.path.exists(candidate):
                        # place logo at top-left with max width
                        max_w = 120
                        max_h = 50
                        canvas_obj.drawImage(candidate, 40, doc_obj.pagesize[1] - max_h - 20, width=max_w, height=max_h, preserveAspectRatio=True, mask='auto')
                except Exception:
                    pass

        doc.build(elements, onFirstPage=_on_first_page)
        buffer.seek(0)
        return buffer
