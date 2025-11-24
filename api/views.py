from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from .pagination import StandardResultsSetPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from .models import Equipment, Maintenance, Photo, Signature, SecondSignature, Report
from .serializers import EquipmentSerializer, MaintenanceSerializer, PhotoSerializer, SignatureSerializer, SecondSignatureSerializer, ReportSerializer
from .permissions import IsAdmin, IsAdminOrTechnician, IsOwnerOrAdmin
from .validators import validate_photo_limit
from .filters import MaintenanceFilter
from .services_main import generate_equipment_report
from django.db.models.signals import pre_save
from django.dispatch import receiver
import boto3
from django.conf import settings
from botocore.client import Config
from django.db.models import Count, Q
from datetime import datetime, timedelta

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all().order_by('-created_at')
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]  # Default base
    # Use standard pagination that accepts `?page_size=` from the client
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Técnicos y admins pueden ver equipos
            self.permission_classes = [IsAdminOrTechnician]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Solo admins pueden crear, editar y eliminar equipos
            self.permission_classes = [IsAdmin]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def maintenances(self, request, pk=None):
        equipment = self.get_object()
        maintenances = equipment.maintenances.all().order_by('-maintenance_date')
        page = self.paginate_queryset(maintenances)
        if page is not None:
            serializer = MaintenanceSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MaintenanceSerializer(maintenances, many=True)
        return Response(serializer.data)

class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all().order_by('-created_at')
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAdminOrTechnician]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MaintenanceFilter
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwnerOrAdmin]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        # Log incoming data for debugging
        print("Request data:", request.data)
        print("Request files:", request.FILES)
        
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        try:
            maintenance = serializer.save()
            maintenance._audit_user = request.user

            # Return the full maintenance data with photos and signatures
            serializer = self.get_serializer(maintenance)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(f"Error creating maintenance: {str(e)}")
            return Response(
                {'error': str(e), 'detail': 'Error al crear el mantenimiento'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        maintenance = self.get_object()
        photos = maintenance.photos.all()
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def upload_photo(self, request, pk=None):
        maintenance = self.get_object()
        validate_photo_limit(maintenance)
        serializer = PhotoSerializer(data={'maintenance': maintenance.id, 'image': request.FILES.get('image')})
        if serializer.is_valid():
            photo = serializer.save()
            photo._audit_user = request.user  # Set user for audit
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReportListView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAdminOrTechnician]

    def get(self, request):
        """
        Listar reportes generados
        """
        reports = Report.objects.all().order_by('-generated_at')
        page = PageNumberPagination().paginate_queryset(reports, request)
        if page is not None:
            serializer = ReportSerializer(page, many=True, context={'request': request})
            return PageNumberPagination().get_paginated_response(serializer.data)
        serializer = ReportSerializer(reports, many=True, context={'request': request})
        return Response(serializer.data)

class ReportGenerateView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAdminOrTechnician]

    def post(self, request):
        """
        Generar reporte PDF de mantenimiento
        """
        maintenance_id = request.data.get('maintenance_id')

        if not maintenance_id:
            return Response(
                {'error': 'maintenance_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from .services.maintenance_serializer import serialize_maintenance
            from .services.report_generators.pdf_generator import PDFGenerator
            from .services.report_generators.excel_generator import ExcelGenerator
            from .services.report_generators.image_generator import ImageGenerator
            from django.core.files.base import ContentFile
            
            # Obtener el mantenimiento
            maintenance = Maintenance.objects.get(id=maintenance_id)

            # Serializar datos y generar según formato solicitado (por defecto pdf)
            data = serialize_maintenance(maintenance_id)
            format_type = request.data.get('format', 'pdf')

            if format_type == 'pdf':
                # Try to include configured logo if available
                logo_path = getattr(settings, 'REPORT_LOGO_PATH', None)
                primary_color = getattr(settings, 'REPORT_PRIMARY_COLOR', None)
                buffer = PDFGenerator().generate(data, logo_path=logo_path, primary_color=primary_color)
                content_type = 'application/pdf'
                ext = 'pdf'
            elif format_type == 'excel':
                buffer = ExcelGenerator().generate(data)
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                ext = 'xlsx'
            elif format_type == 'image':
                buffer = ImageGenerator().generate(data)
                content_type = 'image/png'
                ext = 'png'
            else:
                return Response({'error': 'Formato no soportado'}, status=status.HTTP_400_BAD_REQUEST)

            # Crear el reporte en la base de datos y guardar archivo
            report = Report.objects.create(
                maintenance=maintenance,
                title=f"Reporte de Mantenimiento - {data.get('equipment_code','')}",
                content=maintenance.description or '',
                generated_by=request.user
            )

            filename = f"reporte_mantenimiento_{maintenance.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
            report_field = 'pdf_file' if ext == 'pdf' else f'pdf_file'
            report.pdf_file.save(filename, ContentFile(buffer.read()))

            return Response({
                'id': report.id,
                'pdf_file': request.build_absolute_uri(report.pdf_file.url) if report.pdf_file else None,
                'title': report.title,
                'generated_at': report.generated_at,
            }, status=status.HTTP_201_CREATED)

        except Maintenance.DoesNotExist:
            return Response(
                {'error': 'Mantenimiento no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            import traceback
            print(f"Error generating report: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {'error': f'Error al generar el reporte: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        groups = [group.name for group in user.groups.all()]
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'groups': groups,
        })

class DashboardView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Estadísticas generales del dashboard
        """
        # Build base queryset for maintenances and apply filters from query params
        qs = Maintenance.objects.select_related('equipment', 'sede_rel', 'dependencia_rel', 'subdependencia', 'technician').all()

        # Supported filters (client can send these query params)
        sede_id = request.query_params.get('sede_id') or request.query_params.get('sede')
        dependencia_id = request.query_params.get('dependencia_id') or request.query_params.get('dependencia')
        subdependencia_id = request.query_params.get('subdependencia_id') or request.query_params.get('subdependencia')
        equipment_placa = request.query_params.get('equipment_placa') or request.query_params.get('placa')
        search = request.query_params.get('search')

        if sede_id:
            # prefer FK numeric id
            try:
                sid = int(sede_id)
                qs = qs.filter(sede_rel_id=sid)
            except Exception:
                qs = qs.filter(Q(sede__icontains=sede_id) | Q(sede_rel__nombre__icontains=sede_id))

        if dependencia_id:
            try:
                did = int(dependencia_id)
                qs = qs.filter(dependencia_rel_id=did)
            except Exception:
                qs = qs.filter(Q(dependencia__icontains=dependencia_id) | Q(dependencia_rel__nombre__icontains=dependencia_id))

        if subdependencia_id:
            try:
                sid = int(subdependencia_id)
                qs = qs.filter(subdependencia_id=sid)
            except Exception:
                qs = qs.filter(Q(subdependencia__nombre__icontains=subdependencia_id) | Q(subdependencia__nombre__icontains=subdependencia_id))

        if equipment_placa:
            qs = qs.filter(Q(equipment__code__icontains=equipment_placa) | Q(placa__icontains=equipment_placa))

        if search:
            qs = qs.filter(
                Q(equipment__code__icontains=search) |
                Q(equipment__name__icontains=search) |
                Q(dependencia__icontains=search) |
                Q(sede__icontains=search) |
                Q(subdependencia__icontains=search) |
                Q(description__icontains=search)
            )

        # Totales basados en el queryset filtrado (si no hubo filtros, serán los globales)
        total_maintenances = qs.count()
        total_equipment = qs.values('equipment_id').distinct().count()
        total_incidents = qs.filter(is_incident=True).count()
        pending_maintenances = qs.filter(Q(activities__icontains='pendiente') | Q(status='pending')).distinct().count()

        # Mantenimientos del mes para el queryset
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        maintenances_this_month = qs.filter(created_at__gte=current_month_start).count()

        # Equipos por tipo (top 5) basado en filtered queryset
        equipment_by_type = qs.values('equipment__name').annotate(count=Count('equipment_id')).order_by('-count')[:5]

        # Mantenimientos recientes: siempre limitar a los últimos 5 del queryset
        recent_maintenances = qs.order_by('-created_at')[:5]

        return Response({
            'overview': {
                'total_equipment': total_equipment,
                'total_maintenances': total_maintenances,
                'total_incidents': total_incidents,
                'pending_maintenances': pending_maintenances,
                'maintenances_this_month': maintenances_this_month,
            },
            'equipment_by_type': list(equipment_by_type),
            'recent_maintenances': MaintenanceSerializer(recent_maintenances, many=True).data,
        })


class DashboardEquipmentView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Lista de equipos para el dashboard
        """
        equipment = Equipment.objects.annotate(
            maintenance_count=Count('maintenances')
        ).order_by('-created_at')[:10]
        
        serializer = EquipmentSerializer(equipment, many=True)
        return Response(serializer.data)
