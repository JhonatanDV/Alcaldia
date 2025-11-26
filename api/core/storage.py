"""
Custom storage backends for MinIO
"""
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class MaintenancePhotoStorage(S3Boto3Storage):
    """Storage backend for maintenance photos"""
    bucket_name = settings.MINIO_BUCKET_NAME_PHOTOS
    endpoint_url = settings.MINIO_ENDPOINT
    access_key = settings.MINIO_ACCESS_KEY
    secret_key = settings.MINIO_SECRET_KEY
    default_acl = 'public-read'
    object_parameters = {'CacheControl': 'max-age=86400'}
    file_overwrite = False
    custom_domain = False


class MaintenanceReportStorage(S3Boto3Storage):
    """Storage backend for maintenance reports"""
    bucket_name = settings.MINIO_BUCKET_NAME_REPORTS
    endpoint_url = settings.MINIO_ENDPOINT
    access_key = settings.MINIO_ACCESS_KEY
    secret_key = settings.MINIO_SECRET_KEY
    default_acl = 'public-read'
    object_parameters = {'CacheControl': 'max-age=86400'}
    file_overwrite = False
    custom_domain = False

    def generate_filename(self, filename):
        return filename


class MaintenanceSignatureStorage(S3Boto3Storage):
    """Storage backend for maintenance signatures"""
    bucket_name = settings.MINIO_BUCKET_NAME_SIGNATURES
    endpoint_url = settings.MINIO_ENDPOINT
    access_key = settings.MINIO_ACCESS_KEY
    secret_key = settings.MINIO_SECRET_KEY
    default_acl = 'public-read'
    object_parameters = {'CacheControl': 'max-age=86400'}
    file_overwrite = False
    custom_domain = False


class MaintenanceThumbnailStorage(S3Boto3Storage):
    """Storage backend for maintenance thumbnails"""
    bucket_name = settings.MINIO_BUCKET_NAME_THUMBNAILS
    endpoint_url = settings.MINIO_ENDPOINT
    access_key = settings.MINIO_ACCESS_KEY
    secret_key = settings.MINIO_SECRET_KEY
    default_acl = 'public-read'
    object_parameters = {'CacheControl': 'max-age=86400'}
    file_overwrite = False
    custom_domain = False


class MaintenanceSecondSignatureStorage(S3Boto3Storage):
    """Storage backend for maintenance second signatures"""
    bucket_name = settings.MINIO_BUCKET_NAME_SIGNATURES  # Use same bucket as signatures
    endpoint_url = settings.MINIO_ENDPOINT
    access_key = settings.MINIO_ACCESS_KEY
    secret_key = settings.MINIO_SECRET_KEY
    default_acl = 'public-read'
    object_parameters = {'CacheControl': 'max-age=86400'}
    file_overwrite = False
    custom_domain = False
