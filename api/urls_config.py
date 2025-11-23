"""
URLs para configuración: Sedes, Dependencias, Subdependencias
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_config import SedeViewSet, DependenciaViewSet, SubdependenciaViewSet

router = DefaultRouter()
router.register(r'sedes', SedeViewSet, basename='sede')
router.register(r'dependencias', DependenciaViewSet, basename='dependencia')
router.register(r'subdependencias', SubdependenciaViewSet, basename='subdependencia')

urlpatterns = [
    path('', include(router.urls)),
]
