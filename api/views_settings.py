from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import SiteConfiguration
from .permissions import IsAdmin


class SettingsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        # Return the singleton configuration (create if missing)
        obj, _ = SiteConfiguration.objects.get_or_create(id=1)
        return Response(obj.config)

    def post(self, request):
        # Accept a JSON payload and replace the stored configuration
        obj, _ = SiteConfiguration.objects.get_or_create(id=1)
        data = request.data or {}
        # If the payload contains a top-level key 'user_settings' or 'system_settings', merge
        if isinstance(data, dict) and ('system_settings' in data or 'user_settings' in data):
            # keep existing config and update keys provided
            config = obj.config or {}
            if 'system_settings' in data:
                config['system_settings'] = data['system_settings']
            if 'user_settings' in data:
                config['user_settings'] = data['user_settings']
            obj.config = config
        else:
            # Replace entirely
            obj.config = data
        obj.save()
        return Response(obj.config, status=status.HTTP_200_OK)
