from urllib.parse import urlparse

import boto3

client = boto3.client('s3')


def get_s3_object_as_string(s3uri: str) -> str:
    parsed = urlparse(s3uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip('/')

    response = client.get_object(
        Bucket=bucket,
        Key=key,
    )

    return response['Body'].read().decode('utf-8')

def upload_string_to_s3(s3uri: str, content: str) -> None:
    parsed = urlparse(s3uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip('/')

    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=content.encode('utf-8'),
    )
