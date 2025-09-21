import os
import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

MINIO_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT_URL", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", settings.model_config.get("MINIO_ROOT_USER", "minioadmin"))
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", settings.model_config.get("MINIO_ROOT_PASSWORD", "minioadmin"))


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT_URL,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        region_name="us-east-1",
    )


def create_bucket_if_not_exists(bucket_name: str):
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = int(e.response["Error"]["Code"])
        if error_code == 404:
            s3.create_bucket(Bucket=bucket_name)
        elif error_code == 403:
            # Forbidden, bucket may exist but not owned
            raise
        # else: already exists or other error


def upload_file(file_object, bucket_name: str, object_name: str):
    s3 = get_s3_client()
    s3.upload_fileobj(file_object, bucket_name, object_name)


def generate_presigned_url(bucket_name: str, object_name: str, expiration_seconds: int = 604800) -> str:
    s3 = get_s3_client()
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration_seconds,
        )
        return url
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None
