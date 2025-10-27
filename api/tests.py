from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Equipment, Maintenance, Photo, Signature, AuditLog
from .validators import validate_file_size, validate_file_type, validate_photo_limit
from django.core.exceptions import ValidationError
import json

class ValidatorTests(TestCase):
    def setUp(self):
        self.equipment = Equipment.objects.create(
            code='EQ001',
            name='Test Equipment',
            location='Test Location'
        )
        self.maintenance = Maintenance.objects.create(
            equipment=self.equipment,
            description='Test maintenance',
            maintenance_date='2024-01-01',
            performed_by='Test User'
        )

    def test_validate_file_size_valid(self):
        """Test file size validation with valid size."""
        small_file = SimpleUploadedFile("test.jpg", b"x" * 1024, content_type="image/jpeg")
        try:
            validate_file_size(small_file)
        except ValidationError:
            self.fail("validate_file_size raised ValidationError unexpectedly")

    def test_validate_file_size_invalid(self):
        """Test file size validation with invalid size."""
        large_file = SimpleUploadedFile("test.jpg", b"x" * (6 * 1024 * 1024), content_type="image/jpeg")
        with self.assertRaises(ValidationError):
            validate_file_size(large_file)

    def test_validate_file_type_valid(self):
        """Test file type validation with valid types."""
        valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        for content_type in valid_types:
            with self.subTest(content_type=content_type):
                file_obj = SimpleUploadedFile("test.jpg", b"test", content_type=content_type)
                try:
                    validate_file_type(file_obj)
                except ValidationError:
                    self.fail(f"validate_file_type raised ValidationError for {content_type}")

    def test_validate_file_type_invalid(self):
        """Test file type validation with invalid type."""
        invalid_file = SimpleUploadedFile("test.txt", b"test", content_type="text/plain")
        with self.assertRaises(ValidationError):
            validate_file_type(invalid_file)

    def test_validate_photo_limit_valid(self):
        """Test photo limit validation when under limit."""
        # Should not raise exception
        try:
            validate_photo_limit(self.maintenance)
        except ValidationError:
            self.fail("validate_photo_limit raised ValidationError unexpectedly")

    def test_validate_photo_limit_invalid(self):
        """Test photo limit validation when over limit."""
        # Create 10 photos
        for i in range(10):
            Photo.objects.create(
                maintenance=self.maintenance,
                image=SimpleUploadedFile(f"test{i}.jpg", b"test", content_type="image/jpeg")
            )
        # 11th should fail
        with self.assertRaises(ValidationError):
            validate_photo_limit(self.maintenance)

class MaintenanceAPITests(APITestCase):
    def setUp(self):
        # Create groups
        admin_group = Group.objects.create(name='Admin')
        tech_group = Group.objects.create(name='Technician')

        # Create users
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@test.com'
        )
        self.admin_user.groups.add(admin_group)

        self.tech_user = User.objects.create_user(
            username='tech',
            password='tech123',
            email='tech@test.com'
        )
        self.tech_user.groups.add(tech_group)

        # Create equipment
        self.equipment = Equipment.objects.create(
            code='EQ001',
            name='Test Equipment',
            location='Test Location'
        )

        # Get tokens
        response = self.client.post('/api/token/', {
            'username': 'admin',
            'password': 'admin123'
        })
        self.admin_token = response.data['access']

        response = self.client.post('/api/token/', {
            'username': 'tech',
            'password': 'tech123'
        })
        self.tech_token = response.data['access']

    def test_create_maintenance_with_photos(self):
        """Test creating maintenance with multiple photos."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        # Create maintenance data
        data = {
            'equipment': self.equipment.id,
            'maintenance_type': 'computer',
            'description': 'Test maintenance with photos',
            'maintenance_date': '2024-01-01',
            'performed_by': 'Test Technician',
            'sede': 'Test Sede',
            'dependencia': 'Test Dependencia',
            'oficina': 'Test Oficina',
            'placa': 'Test Placa',
            'hora_inicio': '08:00:00',
            'hora_final': '10:00:00'
        }

        # Create test files - add to data dict for multipart upload
        # Use minimal valid JPEG data
        jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
        data['photos'] = [
            SimpleUploadedFile("photo0.jpg", jpeg_data, content_type="image/jpeg"),
            SimpleUploadedFile("photo1.jpg", jpeg_data, content_type="image/jpeg"),
            SimpleUploadedFile("photo2.jpg", jpeg_data, content_type="image/jpeg")
        ]

        response = self.client.post('/api/maintenances/', data, format='multipart')
        if response.status_code != status.HTTP_201_CREATED:
            print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check maintenance was created
        maintenance = Maintenance.objects.get(description='Test maintenance with photos')
        self.assertEqual(maintenance.photos.count(), 3)

        # Check audit log was created
        audit_logs = AuditLog.objects.filter(model='maintenances', action='CREATE')
        self.assertTrue(audit_logs.exists())

    def test_create_maintenance_photo_limit_exceeded(self):
        """Test that creating maintenance with too many photos fails."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        data = {
            'equipment': self.equipment.id,
            'description': 'Test maintenance',
            'maintenance_date': '2024-01-01',
            'performed_by': 'Test Technician'
        }

        # Create 11 files (exceeds limit)
        data['photos'] = []
        for i in range(11):
            data['photos'].append(SimpleUploadedFile(
                f"photo{i}.jpg",
                b"test image content",
                content_type="image/jpeg"
            ))

        response = self.client.post('/api/maintenances/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_photo_to_maintenance(self):
        """Test uploading a photo to an existing maintenance."""
        # Create maintenance first
        maintenance = Maintenance.objects.create(
            equipment=self.equipment,
            description='Test maintenance',
            maintenance_date='2024-01-01',
            performed_by='Test Technician'
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        # Use the real test image file
        with open('media/test_images/test.jpg', 'rb') as f:
            photo_file = SimpleUploadedFile("test.jpg", f.read(), content_type="image/jpeg")
        data = {'image': photo_file}

        response = self.client.post(
            f'/api/maintenances/{maintenance.id}/upload_photo/',
            data,
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check photo was added
        maintenance.refresh_from_db()
        self.assertEqual(maintenance.photos.count(), 1)

    def test_get_maintenance_photos(self):
        """Test retrieving photos for a maintenance."""
        maintenance = Maintenance.objects.create(
            equipment=self.equipment,
            description='Test maintenance',
            maintenance_date='2024-01-01',
            performed_by='Test Technician'
        )

        # Add photos
        for i in range(2):
            Photo.objects.create(
                maintenance=maintenance,
                image=SimpleUploadedFile(f"photo{i}.jpg", b"content", content_type="image/jpeg")
            )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        response = self.client.get(f'/api/maintenances/{maintenance.id}/photos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_maintenance_filtering(self):
        """Test filtering maintenances by various criteria."""
        # Create multiple maintenances
        Maintenance.objects.create(
            equipment=self.equipment,
            description='Oil change',
            maintenance_date='2024-01-01',
            performed_by='Tech A'
        )
        Maintenance.objects.create(
            equipment=self.equipment,
            description='Filter replacement',
            maintenance_date='2024-01-15',
            performed_by='Tech B'
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        # Filter by performed_by
        response = self.client.get('/api/maintenances/?performed_by=Tech A')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['performed_by'], 'Tech A')

    def test_equipment_maintenances_endpoint(self):
        """Test getting maintenances for a specific equipment."""
        # Create maintenances for the equipment
        for i in range(3):
            Maintenance.objects.create(
                equipment=self.equipment,
                description=f'Maintenance {i}',
                maintenance_date=f'2024-01-0{i+1}',
                performed_by='Test Tech'
            )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        response = self.client.get(f'/api/equipments/{self.equipment.id}/maintenances/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_audit_log_creation(self):
        """Test that audit logs are created for maintenance operations."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        # Create maintenance
        data = {
            'equipment': self.equipment.id,
            'description': 'Audit test maintenance',
            'maintenance_date': '2024-01-01',
            'performed_by': 'Test Technician'
        }

        response = self.client.post('/api/maintenances/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check audit log
        audit_logs = AuditLog.objects.filter(
            user=self.admin_user,
            model='maintenances',
            action='CREATE'
        )
        self.assertTrue(audit_logs.exists())

    def test_permission_admin_access(self):
        """Test that admin can access all endpoints."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')

        # Test equipment creation
        data = {
            'code': 'EQ002',
            'name': 'New Equipment',
            'location': 'New Location'
        }
        response = self.client.post('/api/equipments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_permission_technician_access(self):
        """Test that technician can access maintenance endpoints."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.tech_token}')

        # Test maintenance creation
        data = {
            'equipment': self.equipment.id,
            'description': 'Tech maintenance',
            'maintenance_date': '2024-01-01',
            'performed_by': 'Technician'
        }
        response = self.client.post('/api/maintenances/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_permission_unauthorized_access(self):
        """Test that unauthorized users cannot access protected endpoints."""
        # No credentials
        response = self.client.get('/api/maintenances/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class ReportGenerationTests(APITestCase):
    def setUp(self):
        # Create admin user
        admin_group = Group.objects.create(name='Admin')
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123'
        )
        self.admin_user.groups.add(admin_group)

        # Create equipment and maintenance
        self.equipment = Equipment.objects.create(
            code='EQ001',
            name='Test Equipment'
        )
        self.maintenance = Maintenance.objects.create(
            equipment=self.equipment,
            description='Test maintenance for report',
            maintenance_date='2024-01-01',
            performed_by='Test Tech'
        )

        # Get token
        response = self.client.post('/api/token/', {
            'username': 'admin',
            'password': 'admin123'
        })
        self.token = response.data['access']

    def test_generate_report(self):
        """Test PDF report generation."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        data = {'equipment_id': self.equipment.id, 'date': '2024-01-01'}
        response = self.client.post('/api/reports/generate/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check report was created
        from .models import Report
        report_exists = Report.objects.filter(maintenance=self.maintenance).exists()
        self.assertTrue(report_exists)

    def test_get_reports_list(self):
        """Test retrieving list of generated reports."""
        # Create a report first
        from .models import Report
        from django.core.files.base import ContentFile
        Report.objects.create(
            maintenance=self.maintenance,
            pdf_file=ContentFile(b'test pdf content', name='test.pdf'),
            file_size=100
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        response = self.client.get('/api/reports/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
