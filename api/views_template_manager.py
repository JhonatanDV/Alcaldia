from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Template
from .services.html_pdf_generator import HTMLPDFGenerator
import json
from datetime import datetime


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
@permission_classes([IsAuthenticated])
def upload_template(request):
    try:
        name = request.data.get('name')
        template_type = request.data.get('type')
        html_content = request.data.get('html_content', '')
        css_content = request.data.get('css_content', HTMLPDFGenerator.get_default_css())
        fields_schema = json.loads(request.data.get('fields_schema', '{}')) if request.data.get('fields_schema') else {}
        template_file = request.FILES.get('template_file')

        template = Template.objects.create(
            name=name,
            type=template_type,
            html_content=html_content,
            css_content=css_content,
            fields_schema=fields_schema,
            template_file=template_file
        )

        return Response({
            'id': template.id,
            'name': template.name,
            'message': 'Plantilla creada exitosamente'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_templates(request):
    templates = Template.objects.all().values('id', 'name', 'type', 'description', 'created_at')
    return Response(list(templates))


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_template(request, template_id):
    try:
        template = Template.objects.get(id=template_id)
        template_file_url = None
        try:
            if template.template_file:
                template_file_url = request.build_absolute_uri(template.template_file.url)
        except Exception:
            template_file_url = None

        return Response({
            'id': template.id,
            'name': template.name,
            'type': template.type,
            'description': template.description,
            'html_content': template.html_content,
            'css_content': template.css_content,
            'fields_schema': template.fields_schema,
            'template_file': template_file_url,
        })
    except Template.DoesNotExist:
        return Response({'error': 'Plantilla no encontrada'}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_from_template(request, template_id):
    try:
        template = Template.objects.get(id=template_id)
        data = request.data.get('data', {})

        if template.type == 'pdf':
            pdf_file = HTMLPDFGenerator.render_template(template.html_content, template.css_content, data)
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{template.name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
            return response
        elif template.type == 'excel':
            # For excel templates you can implement mapping logic here or use a stored xlsx
            return Response({'error': 'Excel templates not implemented yet'}, status=501)
        else:
            return Response({'error': 'Tipo de plantilla no soportado'}, status=400)
    except Template.DoesNotExist:
        return Response({'error': 'Plantilla no encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_template(request, template_id):
    try:
        template = Template.objects.get(id=template_id)

        template.name = request.data.get('name', template.name)
        template.html_content = request.data.get('html_content', template.html_content)
        template.css_content = request.data.get('css_content', template.css_content)
        fs = request.data.get('fields_schema')
        template.fields_schema = json.loads(fs) if isinstance(fs, str) and fs else (fs or template.fields_schema)
        template.save()
        return Response({'message': 'Plantilla actualizada exitosamente'})
    except Template.DoesNotExist:
        return Response({'error': 'Plantilla no encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_template(request, template_id):
    try:
        template = Template.objects.get(id=template_id)
        template.delete()
        return Response({'message': 'Plantilla eliminada exitosamente'})
    except Template.DoesNotExist:
        return Response({'error': 'Plantilla no encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
