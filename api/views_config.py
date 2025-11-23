"""
Vistas para la gestión de configuraciones: Sedes, Dependencias y Subdependencias
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .models import Sede, Dependencia, Subdependencia
from .serializers import SedeSerializer, DependenciaSerializer, SubdependenciaSerializer
from .permissions import IsAdmin


class SedeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las sedes de la alcaldía.
    Solo administradores pueden crear, editar y eliminar.
    """
    queryset = Sede.objects.all().order_by('nombre')
    serializer_class = SedeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activo', 'codigo']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdmin]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def dependencias(self, request, pk=None):
        """Obtener todas las dependencias de una sede"""
        sede = self.get_object()
        dependencias = sede.dependencias.filter(activo=True)
        serializer = DependenciaSerializer(dependencias, many=True)
        return Response(serializer.data)


class DependenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las dependencias asociadas a las sedes.
    Solo administradores pueden crear, editar y eliminar.
    """
    queryset = Dependencia.objects.select_related('sede').all().order_by('nombre')
    serializer_class = DependenciaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sede', 'activo', 'codigo']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdmin]
        return super().get_permissions()

    @action(detail=True, methods=['get'])
    def subdependencias(self, request, pk=None):
        """Obtener todas las subdependencias de una dependencia"""
        dependencia = self.get_object()
        subdependencias = dependencia.subdependencias.filter(activo=True)
        serializer = SubdependenciaSerializer(subdependencias, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def por_sede(self, request):
        """Filtrar dependencias por sede"""
        sede_id = request.query_params.get('sede_id')
        if not sede_id:
            return Response(
                {'error': 'Se requiere el parámetro sede_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        dependencias = self.queryset.filter(sede_id=sede_id, activo=True)
        serializer = self.get_serializer(dependencias, many=True)
        return Response(serializer.data)


class SubdependenciaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las subdependencias asociadas a las dependencias.
    Solo administradores pueden crear, editar y eliminar.
    """
    queryset = Subdependencia.objects.select_related('dependencia__sede').all().order_by('nombre')
    serializer_class = SubdependenciaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dependencia', 'activo', 'codigo']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdmin]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def por_dependencia(self, request):
        """Filtrar subdependencias por dependencia"""
        dependencia_id = request.query_params.get('dependencia_id')
        if not dependencia_id:
            return Response(
                {'error': 'Se requiere el parámetro dependencia_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        subdependencias = self.queryset.filter(dependencia_id=dependencia_id, activo=True)
        serializer = self.get_serializer(subdependencias, many=True)
        return Response(serializer.data)
