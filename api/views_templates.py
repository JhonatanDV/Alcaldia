from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
import io

from .template_generators import ExcelTemplateGenerator, PDFTemplateGenerator


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_excel(request):
    try:
        data = request.data
        template_type = data.get('template_type', 'default')
        payload = data.get('data', {})

        generator = ExcelTemplateGenerator()

        if template_type == 'invoice':
            generator.fill_template({
                'A1': 'FACTURA',
                'A3': f"Cliente: {payload.get('client_name', '')}",
                'A4': f"Fecha: {datetime.now().strftime('%Y-%m-%d')}",
            })
            items = payload.get('items', [])
            generator.create_table(start_row=6, headers=['Item', 'Cantidad', 'Precio', 'Total'], rows=items)

        elif template_type == 'report':
            generator.fill_template({
                'cells': [
                    {'cell': 'A1', 'value': payload.get('title', ''), 'bold': True, 'align': 'center'},
                    {'cell': 'A3', 'value': f"Generado: {datetime.now()}", 'bold': False}
                ]
            })

        else:
            # default: try to fill raw mapping
            generator.fill_template(payload)

        file_bytes = generator.get_file()
        response = HttpResponse(file_bytes.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{template_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'
        return response

    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_pdf(request):
    try:
        data = request.data
        template_type = data.get('template_type', 'default')
        payload = data.get('data', {})

        generator = PDFTemplateGenerator()

        if template_type == 'report':
            generator.fill_template({
                'title': payload.get('title', ''),
                'sections': [
                    {'type': 'text', 'content': f"Fecha: {datetime.now().strftime('%Y-%m-%d')}", 'bold': True},
                    {'type': 'text', 'content': payload.get('description', '')},
                    {'type': 'table', 'headers': payload.get('table_headers', ['Col1', 'Col2']), 'rows': payload.get('table_data', [])}
                ]
            })
        else:
            generator.fill_template(payload)

        file_bytes = generator.get_file()
        response = HttpResponse(file_bytes.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{template_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        return response

    except Exception as e:
        return Response({'error': str(e)}, status=400)
