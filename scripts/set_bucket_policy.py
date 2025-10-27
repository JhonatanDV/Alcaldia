"""
Script to set public read policy on MinIO buckets
"""
import boto3
import json
from botocore.client import Config
from core.settings import MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET_NAME_REPORTS

def set_bucket_policy():
    """Set public read policy on maintenance-reports bucket"""
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=MINIO_ENDPOINT,
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )

        # Set bucket policy for public read
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{MINIO_BUCKET_NAME_REPORTS}/*"
                }
            ]
        }

        s3_client.put_bucket_policy(Bucket=MINIO_BUCKET_NAME_REPORTS, Policy=json.dumps(policy))
        print(f"✓ Public read policy set on bucket '{MINIO_BUCKET_NAME_REPORTS}'")

    except Exception as e:
        print(f"✗ Error setting bucket policy: {e}")

if __name__ == '__main__':
    set_bucket_policy()
