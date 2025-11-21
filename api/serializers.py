from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import (
    Equipment, 
    Maintenance, 
    Incident,
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
    class Meta:
        model = Signature
        fields = '__all__'


class SecondSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondSignature
        fields = '__all__'


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
