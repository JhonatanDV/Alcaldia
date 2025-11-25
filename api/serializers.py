from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import (
    Equipment, 
    Maintenance, 
    Incident,
    Photo,
    Signature,
    SecondSignature,
    Report,
    Sede,
    Dependencia,
    Subdependencia
)


class SedeSerializer(serializers.ModelSerializer):
    dependencias_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Sede
        # Exponer sólo los campos requeridos por UI: id, nombre y direccion
        fields = ['id', 'nombre', 'direccion', 'activo', 'dependencias_count']
    
    def get_dependencias_count(self, obj):
        return obj.dependencias.count()


class DependenciaSerializer(serializers.ModelSerializer):
    sede_nombre = serializers.CharField(source='sede.nombre', read_only=True)
    subdependencias_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Dependencia
        # Sólo exponer id, nombre, direccion (direccion se tomará desde la sede) y sede
        fields = ['id', 'nombre', 'sede', 'sede_nombre', 'activo', 'subdependencias_count']
    
    def get_subdependencias_count(self, obj):
        return obj.subdependencias.count()


class SubdependenciaSerializer(serializers.ModelSerializer):
    dependencia_nombre = serializers.CharField(source='dependencia.nombre', read_only=True)
    sede_nombre = serializers.CharField(source='dependencia.sede.nombre', read_only=True)
    
    class Meta:
        model = Subdependencia
        # Exponer sólo id, nombre y dependencia
        fields = ['id', 'nombre', 'dependencia', 'dependencia_nombre', 'sede_nombre', 'activo']


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = '__all__'


class SignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = '__all__'


class SecondSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondSignature
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    generado_por_nombre = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = '__all__'

    def get_generado_por_nombre(self, obj):
        user = getattr(obj, 'generated_by', None) or getattr(obj, 'generado_por', None)
        if user:
            return f"{user.first_name} {user.last_name}".strip() or user.username
        return None

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.pdf_file:
            try:
                url = obj.pdf_file.url
                if request:
                    return request.build_absolute_uri(url)
                return url
            except Exception:
                return None
        return None


class RoleSerializer(serializers.ModelSerializer):
    """Serializer para roles (Django Groups) con terminología más clara"""
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['id', 'name', 'user_count']

    def get_user_count(self, obj):
        return obj.user_set.count()


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_active', 'is_staff', 'is_superuser', 'roles', 'date_joined']
        read_only_fields = ['id', 'date_joined']

    def get_roles(self, obj):
        return [{'id': group.id, 'name': group.name} for group in obj.groups.all()]


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
    equipo_placa = serializers.SerializerMethodField()
    equipo_tipo = serializers.CharField(source='equipment.name', read_only=True)
    equipo_marca = serializers.CharField(source='equipment.brand', read_only=True)
    equipo_modelo = serializers.CharField(source='equipment.model', read_only=True)
    tecnico_nombre = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True, read_only=True)
    signatures = SignatureSerializer(many=True, read_only=True)
    equipment = serializers.PrimaryKeyRelatedField(
        queryset=Equipment.objects.all(),
        required=True
    )

    class Meta:
        model = Maintenance
        fields = '__all__'

    def get_equipo_placa(self, obj):
        if obj.equipment:
            return obj.equipment.code or obj.equipment.serial_number or obj.placa or 'N/A'
        return obj.placa or 'N/A'

    def get_tecnico_nombre(self, obj):
        if obj.technician:
            return f"{obj.technician.first_name} {obj.technician.last_name}".strip() or obj.technician.username
        return None

    def create(self, validated_data):
        request = self.context.get('request')
        
        # Extract and validate activities
        activities = validated_data.get('activities', {})
        if isinstance(activities, str):
            import json
            try:
                activities = json.loads(activities)
            except:
                activities = {}
        validated_data['activities'] = activities
        
        # Convert is_incident string to boolean if needed
        if 'is_incident' in validated_data:
            is_incident = validated_data.get('is_incident')
            if isinstance(is_incident, str):
                validated_data['is_incident'] = is_incident.lower() == 'true'
        
        maintenance = Maintenance.objects.create(**validated_data)

        # Handle photos if present
        if request and hasattr(request, 'FILES'):
            photos = request.FILES.getlist('photos')
            for photo in photos:
                Photo.objects.create(
                    maintenance=maintenance, 
                    photo=photo, 
                    uploaded_by=request.user if request else None
                )
            
            # Handle signature
            signature = request.FILES.get('signature')
            if signature:
                signer_name = 'Técnico'
                if maintenance.technician:
                    signer_name = maintenance.technician.get_full_name() or maintenance.technician.username
                Signature.objects.create(
                    maintenance=maintenance,
                    signature_image=signature,
                    signer_name=signer_name,
                    signer_role='Técnico'
                )
            
            # Handle second signature
            second_signature = request.FILES.get('second_signature')
            if second_signature:
                SecondSignature.objects.create(
                    maintenance=maintenance,
                    signature_image=second_signature,
                    signer_name='Usuario',
                    signer_role='Usuario del equipo'
                )

        return maintenance


class IncidentSerializer(serializers.ModelSerializer):
    equipo_placa = serializers.CharField(source='equipment.code', read_only=True)
    equipo_tipo = serializers.CharField(source='equipment.name', read_only=True)
    reportado_por_nombre = serializers.SerializerMethodField()
    asignado_a_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = '__all__'

    def get_reportado_por_nombre(self, obj):
        user = getattr(obj, 'reported_by', None) or getattr(obj, 'reportado_por', None)
        if user:
            return f"{user.first_name} {user.last_name}".strip() or user.username
        return None

    def get_asignado_a_nombre(self, obj):
        user = getattr(obj, 'assigned_to', None) or getattr(obj, 'asignado_a', None)
        if user:
            return f"{user.first_name} {user.last_name}".strip() or user.username
        return None
