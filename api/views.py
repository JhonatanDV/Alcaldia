from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from .models import Equipment, Maintenance, Photo, Signature, SecondSignature, Report
from .serializers import EquipmentSerializer, MaintenanceSerializer, PhotoSerializer, SignatureSerializer, SecondSignatureSerializer, ReportSerializer
from .permissions import IsAdmin, IsAdminOrTechnician, IsOwnerOrAdmin
from .validators import validate_photo_limit
from .filters import MaintenanceFilter
from .services import generate_equipment_report
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
    permission_classes = [IsAdmin]  # Default para acciones restrictivas
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'create']:
            # Técnicos pueden ver y crear equipos
            self.permission_classes = [IsAdminOrTechnician]
        # update y destroy quedan con IsAdmin (solo admins)
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
    pagination_class = PageNumberPagination

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsOwnerOrAdmin]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        maintenance = serializer.save()
        maintenance._audit_user = request.user

        # Return the full maintenance data with photos and signatures
        serializer = self.get_serializer(maintenance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

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
        Generar reporte de mantenimiento de equipo
        """
        equipment_id = request.data.get('equipment_id')
        date = request.data.get('date')

        if not equipment_id or not date:
            return Response(
                {'error': 'equipment_id y date son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Convert date to start and end of day
            from datetime import datetime
            start_date = datetime.strptime(date, '%Y-%m-%d').date()
            end_date = start_date

            report = generate_equipment_report(
                equipment_id=int(equipment_id),
                start_date=start_date,
                end_date=end_date,
                user=request.user
            )

            return Response({
                'id': report.id,
                'pdf_file': report.pdf_file.url,
                'created_at': report.generated_at,
                'expires_at': report.expires_at
            }, status=status.HTTP_201_CREATED)

        except Equipment.DoesNotExist:
            return Response(
                {'error': 'Equipo no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
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
        # Total de equipos
        total_equipment = Equipment.objects.count()
        
        # Total de mantenimientos
        total_maintenances = Maintenance.objects.count()
        
        # Mantenimientos pendientes
        pending_maintenances = Maintenance.objects.filter(
            Q(activities__icontains='pendiente') | Q(status='pending')
        ).distinct().count()
        
        # Mantenimientos del mes actual
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        maintenances_this_month = Maintenance.objects.filter(
            created_at__gte=current_month_start
        ).count()
        
        # Equipos por tipo/categoría (si existe)
        equipment_by_type = Equipment.objects.values('name').annotate(
            count=Count('id')
        )[:5]  # Top 5
        
        # Mantenimientos recientes
        recent_maintenances = Maintenance.objects.select_related(
            'equipment', 'technician'
        ).order_by('-created_at')[:5]
        
        return Response({
            'total_equipment': total_equipment,
            'total_maintenances': total_maintenances,
            'pending_maintenances': pending_maintenances,
            'maintenances_this_month': maintenances_this_month,
            'equipment_by_type': list(equipment_by_type),
            'recent_maintenances': MaintenanceSerializer(
                recent_maintenances, many=True
            ).data
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
