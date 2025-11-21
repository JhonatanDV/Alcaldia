from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status, views, permissions


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Agregar información del usuario y su rol
        user = self.user
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        
        # Determinar el rol del usuario (prioridad: superuser > staff > grupos)
        if user.is_superuser:
            data['role'] = 'admin'
        elif user.is_staff or user.groups.filter(name='Admin').exists():
            data['role'] = 'admin'
        elif user.groups.filter(name='Tecnico').exists():
            data['role'] = 'technician'
        else:
            data['role'] = 'user'
        
        # Debug: Log role assignment
        print(f"User: {user.username}, is_staff: {user.is_staff}, is_superuser: {user.is_superuser}")
        print(f"Groups: {[g.name for g in user.groups.all()]}")
        print(f"Assigned role: {data['role']}")
        
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
