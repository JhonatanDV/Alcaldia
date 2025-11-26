"""
Script para verificar y configurar MinIO
"""
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

# Configuración de MinIO
MINIO_ENDPOINT = 'http://localhost:9000'
MINIO_ACCESS_KEY = 'minioadmin'
MINIO_SECRET_KEY = 'minioadmin'

# Nombres de los buckets
BUCKETS = [
    'maintenance-photos',
    'maintenance-reports',
    'maintenance-signatures',
    'maintenance-thumbnails'
]

def setup_minio():
    """Configurar MinIO y crear buckets necesarios"""
    try:
        # Crear cliente S3 para MinIO
        s3_client = boto3.client(
            's3',
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        
        print("✓ Conexión exitosa con MinIO")
        
        # Listar buckets existentes
        existing_buckets = [bucket['Name'] for bucket in s3_client.list_buckets()['Buckets']]
        print(f"\nBuckets existentes: {existing_buckets}")
        
        # Crear buckets si no existen
        for bucket_name in BUCKETS:
            if bucket_name not in existing_buckets:
                try:
                    s3_client.create_bucket(Bucket=bucket_name)
                    print(f"✓ Bucket '{bucket_name}' creado exitosamente")
                except ClientError as e:
                    print(f"✗ Error al crear bucket '{bucket_name}': {e}")
            else:
                print(f"✓ Bucket '{bucket_name}' ya existe")
        
        # Configurar política pública para los buckets (opcional)
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*" for bucket_name in BUCKETS]
                }
            ]
        }
        
        print("\n✓ Configuración de MinIO completada")
        print("\nIMPORTANTE: Los reportes ahora se guardarán en MinIO, NO en el sistema de archivos local.")
        print(f"Puedes acceder a MinIO en: {MINIO_ENDPOINT}")
        print(f"Usuario: {MINIO_ACCESS_KEY}")
        
    except Exception as e:
        print(f"\n✗ Error al conectar con MinIO: {e}")
        print("\nAsegúrate de que MinIO esté corriendo en http://localhost:9000")
        print("Puedes iniciar MinIO con Docker usando:")
        print("docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ':9001'")

if __name__ == '__main__':
    setup_minio()
