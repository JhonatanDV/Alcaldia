from rest_framework import serializers
from .models import Equipment, Maintenance, Photo, Signature, SecondSignature, Report
from .validators import validate_file_size, validate_file_type, validate_photo_limit

class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_file_size, validate_file_type])

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
    file_url = serializers.SerializerMethodField()
    equipment = serializers.SerializerMethodField()
    generated_by = serializers.SerializerMethodField()
    report_data = serializers.JSONField()
    created_at = serializers.DateTimeField(source='generated_at')
    expires_at = serializers.DateTimeField()

    class Meta:
        model = Report
        fields = ['id', 'equipment', 'generated_by', 'report_data', 'pdf_file', 'created_at', 'expires_at', 'file_url']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if request and obj.pdf_file:
            # Ensure storage is properly initialized
            if isinstance(obj.pdf_file.storage, str):
                from core.storage import MaintenanceReportStorage
                obj.pdf_file.storage = MaintenanceReportStorage()
            return request.build_absolute_uri(obj.pdf_file.url)
        return obj.pdf_file.url if obj.pdf_file else None

    def get_equipment(self, obj):
        if obj.maintenance and obj.maintenance.equipment:
            return {
                'id': obj.maintenance.equipment.id,
                'code': obj.maintenance.equipment.code,
                'name': obj.maintenance.equipment.name
            }
        return None

    def get_generated_by(self, obj):
        if obj.generated_by:
            return {
                'id': obj.generated_by.id,
                'username': obj.generated_by.username
            }
        return None

class MaintenanceSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True)
    signature = SignatureSerializer(read_only=True)
    second_signature = SecondSignatureSerializer(read_only=True)
    report = ReportSerializer(read_only=True)

    class Meta:
        model = Maintenance
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get('request') and self.context['request'].method in ['POST', 'PUT', 'PATCH']:
            # For write operations, make photos writable
            self.fields['photos'] = serializers.ListField(
                child=serializers.ImageField(validators=[validate_file_size, validate_file_type]),
                required=False,
                write_only=True
            )
            self.fields['signature'] = serializers.ImageField(
                required=False,
                write_only=True,
                validators=[validate_file_size, validate_file_type]
            )
            self.fields['second_signature'] = serializers.ImageField(
                required=False,
                write_only=True,
                validators=[validate_file_size, validate_file_type]
            )

    def create(self, validated_data):
        # Remove photos from validated_data since it's handled separately
        validated_data.pop('photos', None)
        validated_data.pop('signature', None)
        validated_data.pop('second_signature', None)

        # Parse activities if it's a string
        if isinstance(validated_data.get('activities'), str):
            import json
            validated_data['activities'] = json.loads(validated_data['activities'])

        photos_data = self.context['request'].FILES.getlist('photos')
        signature_data = self.context['request'].FILES.get('signature')
        second_signature_data = self.context['request'].FILES.get('second_signature')

        maintenance = Maintenance.objects.create(**validated_data)

        # Create photos and add to maintenance
        for photo_data in photos_data:
            Photo.objects.create(maintenance=maintenance, image=photo_data)

        # Create signature if provided
        if signature_data:
            Signature.objects.create(maintenance=maintenance, image=signature_data)

        # Create second signature if provided
        if second_signature_data:
            SecondSignature.objects.create(maintenance=maintenance, image=second_signature_data)

        return maintenance

    def validate(self, data):
        is_incident = data.get('is_incident', False)

        # Modo Normal: All fields mandatory except photos
        if not is_incident:
            required_fields = [
                'maintenance_type', 'description', 'maintenance_date', 'performed_by',
                'sede', 'dependencia', 'oficina', 'placa', 'hora_inicio', 'hora_final'
            ]
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError(f"{field} is required in Normal mode.")

        # Modo Incidencia: Reduced mandatory fields
        else:
            required_fields_incident = ['description']  # Only incident annotations required
            for field in required_fields_incident:
                if not data.get(field):
                    raise serializers.ValidationError(f"{field} is required in Incident mode.")

        # Check if maintenance already exists for this equipment on this date
        equipment = data.get('equipment')
        maintenance_date = data.get('maintenance_date')
        if self.instance is None and Maintenance.objects.filter(equipment=equipment, maintenance_date=maintenance_date).exists():
            raise serializers.ValidationError("Maintenance already exists for this equipment on this date.")

        return data

class EquipmentSerializer(serializers.ModelSerializer):
    maintenances = MaintenanceSerializer(many=True, read_only=True)

    class Meta:
        model = Equipment
        fields = '__all__'

class ReportCreateSerializer(serializers.Serializer):
    maintenance_id = serializers.IntegerField()

    def validate_maintenance_id(self, value):
        try:
            maintenance = Maintenance.objects.get(id=value)
            # Check if report already exists
            if hasattr(maintenance, 'report'):
                raise serializers.ValidationError("Report already exists for this maintenance.")
            return value
        except Maintenance.DoesNotExist:
            raise serializers.ValidationError("Maintenance not found.")
