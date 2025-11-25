from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status, views, permissions
import traceback


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


@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            # Log raw body and a few useful headers for debugging
            body_preview = request.body.decode('utf-8', errors='replace')[:2000]
        except Exception:
            body_preview = '<unavailable>'
        print('--- Token endpoint received POST ---')
        print('BODY PREVIEW:', body_preview)
        print('Origin header:', request.META.get('HTTP_ORIGIN'))
        print('Content-Type:', request.META.get('CONTENT_TYPE'))
        print('Authorization header present:', 'HTTP_AUTHORIZATION' in request.META)
        # Inspect serializer state to capture validation errors
        try:
            serializer = self.get_serializer(data=request.data)
            print('Serializer initial_data:', getattr(serializer, 'initial_data', None))
            try:
                serializer.is_valid(raise_exception=True)
            except Exception as ser_exc:
                print('Serializer is_valid() raised. Errors:')
                try:
                    print(serializer.errors)
                except Exception:
                    print('<could not read serializer.errors>')
                traceback.print_exc()
                return Response(getattr(serializer, 'errors', {'detail': 'Invalid data'}), status=status.HTTP_400_BAD_REQUEST)

            # If valid, return the validated data (tokens)
            print('Serializer validated_data keys:', list(getattr(serializer, 'validated_data', {}).keys()))
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        except Exception:
            print('Unexpected error in token post handler:')
            traceback.print_exc()
            return super().post(request, *args, **kwargs)


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
