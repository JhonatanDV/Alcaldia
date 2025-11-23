"""
Vista de prueba para debuggear autenticación JWT
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status


class TestAuthView(APIView):
    """
    Vista de prueba para verificar autenticación
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retorna información del usuario autenticado
        """
        return Response({
            'message': 'Autenticación exitosa',
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'is_staff': request.user.is_staff,
                'is_superuser': request.user.is_superuser,
            }
        }, status=status.HTTP_200_OK)


class TestPublicView(APIView):
    """
    Vista pública sin autenticación
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """
        Vista pública para verificar que el servidor funciona
        """
        return Response({
            'message': 'Vista pública funcionando correctamente'
        }, status=status.HTTP_200_OK)
