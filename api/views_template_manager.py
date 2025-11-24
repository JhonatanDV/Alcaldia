from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Template
from .models import ReportTemplate
import json
from datetime import datetime

try:
    from .services.html_pdf_generator import HTMLPDFGenerator
except Exception:
    HTMLPDFGenerator = None

# Fallback simple generator using ReportLab (pure Python). This avoids
# native deps on environments like Windows. reportlab must be installed
# in the virtualenv for this to work.
try:
    from .services.reportlab_pdf_generator import ReportLabPDFGenerator
except Exception:
    ReportLabPDFGenerator = None

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
        html_content = request.data.get('html_content', '')
        # Import HTMLPDFGenerator lazily because WeasyPrint (used by it)
        # may not be installed in the environment (common on Windows).
        try:
            from .services.html_pdf_generator import HTMLPDFGenerator
            default_css = HTMLPDFGenerator.get_default_css()
        except Exception:
            default_css = ''

        css_content = request.data.get('css_content', default_css)
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
def get_template(request, template_key):
    try:
        # Allow numeric id or textual key (name)
        if isinstance(template_key, str) and template_key.isdigit():
            template = Template.objects.get(id=int(template_key))
        else:
            template = Template.objects.filter(name=template_key).first()
            if not template:
                # fallback: try exact match on id as int conversion
                try:
                    template = Template.objects.get(id=int(template_key))
                except Exception:
                    template = None

        if not template:
            return Response({'error': 'Plantilla no encontrada'}, status=404)
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
def generate_from_template(request, template_key):
    try:
        # Resolve template by id or name
        if isinstance(template_key, str) and template_key.isdigit():
            template = Template.objects.get(id=int(template_key))
        else:
            template = Template.objects.filter(name=template_key).first()
            if not template:
                try:
                    template = Template.objects.get(id=int(template_key))
                except Exception:
                    template = None

        if not template:
            return Response({'error': 'Plantilla no encontrada'}, status=404)
        data = request.data.get('data', {})

        if template.type == 'pdf':
            # Prefer WeasyPrint-based generator (HTMLPDFGenerator). If no
            # WeasyPrint available, try ReportLab fallback which produces a
            # basic PDF rendering of the template content. If the template
            # has an uploaded `template_file` (image) and the client sends
            # overlay specs, the ReportLab fallback will compose text over
            # the image using percentage coordinates.
            # Extract overlays from request data if present. Expect a list of
            # objects: { text, x_pct, y_pct, font_size }
            overlays = None
            try:
                # overlays may be sent as JSON string or as a JSON body field
                overlays_field = request.data.get('_overlays') or request.data.get('overlays')
                if overlays_field:
                    if isinstance(overlays_field, str):
                        import json as _json
                        overlays = _json.loads(overlays_field)
                    else:
                        overlays = overlays_field
            except Exception:
                overlays = None

            background_bytes = None
            try:
                if template.template_file:
                    # Read the file content (works for local storage or FileStorage)
                    template.template_file.open('rb')
                    background_bytes = template.template_file.read()
                    template.template_file.close()
            except Exception:
                background_bytes = None

            if HTMLPDFGenerator:
                # HTML generator does not support image-overlay in this simple path
                pdf_file = HTMLPDFGenerator.render_template(template.html_content, template.css_content, data)
            elif ReportLabPDFGenerator:
                pdf_file = ReportLabPDFGenerator.render_template(
                    template.html_content,
                    template.css_content,
                    data,
                    background_bytes=background_bytes,
                    overlays=overlays
                )
            else:
                return Response({'error': 'Generación de PDF no disponible en este entorno.'}, status=501)
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sample_template_data(request):
    """Devuelve datos de ejemplo serializados para un mantenimiento dado.

    Query params:
      - maintenance_id: int (opcional). Si no se provee, se devuelve el último mantenimiento del usuario.
    """
    maintenance_id = request.query_params.get('maintenance_id')
    try:
        from .services.maintenance_serializer import serialize_maintenance
    except Exception:
        return Response({'error': 'Serializer de mantenimiento no disponible'}, status=500)

    if maintenance_id:
        try:
            data = serialize_maintenance(int(maintenance_id))
            return Response(data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    # If no maintenance_id provided, attempt to return most recent maintenance
    try:
        from .models import Maintenance
        m = Maintenance.objects.order_by('-created_at').first()
        if not m:
            return Response({'error': 'No hay mantenimientos disponibles para generar datos de ejemplo'}, status=404)
        data = serialize_maintenance(m.id)
        return Response(data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_template(request, template_key):
    try:
        if isinstance(template_key, str) and template_key.isdigit():
            template = Template.objects.get(id=int(template_key))
        else:
            template = Template.objects.filter(name=template_key).first()
            if not template:
                try:
                    template = Template.objects.get(id=int(template_key))
                except Exception:
                    template = None

        if not template:
            return Response({'error': 'Plantilla no encontrada'}, status=404)

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
def delete_template(request, template_key):
    try:
        if isinstance(template_key, str) and template_key.isdigit():
            template = Template.objects.get(id=int(template_key))
        else:
            template = Template.objects.filter(name=template_key).first()
            if not template:
                try:
                    template = Template.objects.get(id=int(template_key))
                except Exception:
                    template = None

        if not template:
            return Response({'error': 'Plantilla no encontrada'}, status=404)
        template.delete()
        return Response({'message': 'Plantilla eliminada exitosamente'})
    except Template.DoesNotExist:
        return Response({'error': 'Plantilla no encontrada'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_template(request):
    """Return the active report template and the available PDF generator info."""
    active = ReportTemplate.objects.filter(is_active=True).order_by('-updated_at').first()
    generator = 'reportlab'
    try:
        from .services.html_pdf_generator import HTMLPDFGenerator
        if HTMLPDFGenerator:
            generator = 'weasyprint'
    except Exception:
        generator = 'reportlab'

    if not active:
        return Response({'template': None, 'generator': generator})

    return Response({
        'template': {
            'id': active.id,
            'name': active.name,
            'description': active.description,
            'is_active': active.is_active,
        },
        'generator': generator
    })
