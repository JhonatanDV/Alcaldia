from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import (
    Equipment, 
    Maintenance, 
    Incident, 
    MaintenanceReport,
    Photo,
    Signature,
    SecondSignature,
    Report
)


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'


class SignatureSerializer(serializers.ModelSerializer):
    firmante_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Signature
        fields = '__all__'

    def get_firmante_nombre(self, obj):
        if obj.firmante:
            return f"{obj.firmante.first_name} {obj.firmante.last_name}".strip() or obj.firmante.username
        return None


class SecondSignatureSerializer(serializers.ModelSerializer):
    firmante_nombre = serializers.SerializerMethodField()

    class Meta:
        model = SecondSignature
        fields = '__all__'

    def get_firmante_nombre(self, obj):
        if obj.firmante:
            return f"{obj.firmante.first_name} {obj.firmante.last_name}".strip() or obj.firmante.username
        return None


class ReportSerializer(serializers.ModelSerializer):
    generado_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = '__all__'

    def get_generado_por_nombre(self, obj):
        if obj.generado_por:
            return f"{obj.generado_por.first_name} {obj.generado_por.last_name}".strip() or obj.generado_por.username
        return None


class GroupSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'user_count']

    def get_user_count(self, obj):
        return obj.user_set.count()


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_active', 'is_staff', 'is_superuser', 'groups', 'date_joined']
        read_only_fields = ['id', 'date_joined']

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 
                  'password', 'confirm_password', 'is_active', 'is_staff']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'is_active', 'is_staff']


class EquipmentSerializer(serializers.ModelSerializer):
    maintenance_count = serializers.SerializerMethodField()
    incident_count = serializers.SerializerMethodField()

    class Meta:
        model = Equipment
        fields = '__all__'

    def get_maintenance_count(self, obj):
        return obj.maintenances.count()

    def get_incident_count(self, obj):
        return obj.incidents.count()


class MaintenanceSerializer(serializers.ModelSerializer):
    equipo_placa = serializers.CharField(source='equipo.placa', read_only=True)
    equipo_tipo = serializers.CharField(source='equipo.tipo', read_only=True)
    tecnico_nombre = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)
    signatures = SignatureSerializer(many=True, read_only=True)

    class Meta:
        model = Maintenance
        fields = '__all__'

    def get_tecnico_nombre(self, obj):
        if obj.technician:
            return f"{obj.technician.first_name} {obj.technician.last_name}".strip() or obj.technician.username
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        maintenance = Maintenance.objects.create(**validated_data)

        # Handle photos if present
        if request and hasattr(request, 'FILES'):
            photos = request.FILES.getlist('photos')
            for photo in photos:
                Photo.objects.create(maintenance=maintenance, photo=photo, uploaded_by=request.user if request else None)

        return maintenance


class IncidentSerializer(serializers.ModelSerializer):
    equipo_placa = serializers.CharField(source='equipo.placa', read_only=True)
    equipo_tipo = serializers.CharField(source='equipo.tipo', read_only=True)
    reportado_por_nombre = serializers.SerializerMethodField()
    asignado_a_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = '__all__'

    def get_reportado_por_nombre(self, obj):
        if obj.reportado_por:
            return f"{obj.reportado_por.first_name} {obj.reportado_por.last_name}".strip() or obj.reportado_por.username
        return None

    def get_asignado_a_nombre(self, obj):
        if obj.asignado_a:
            return f"{obj.asignado_a.first_name} {obj.asignado_a.last_name}".strip() or obj.asignado_a.username
        return None


class MaintenanceReportSerializer(serializers.ModelSerializer):
    maintenance_details = MaintenanceSerializer(source='maintenance', read_only=True)
    generated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceReport
        fields = '__all__'

    def get_generated_by_name(self, obj):
        if obj.generated_by:
            return f"{obj.generated_by.first_name} {obj.generated_by.last_name}".strip() or obj.generated_by.username
        return None
