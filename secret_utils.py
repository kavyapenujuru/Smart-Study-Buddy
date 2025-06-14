import boto3
import json
import os

def get_openai_api_key(secret_name=None, region_name=None):
    if not secret_name:
        secret_name = os.environ.get("OPENAI_SECRET_NAME", "SmartStudyBuddy/OpenAI")
    if not region_name:
        region_name = os.environ.get("AWS_REGION", "us-east-1")
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    response = client.get_secret_value(SecretId=secret_name)
    secret = response['SecretString']
    secret_dict = json.loads(secret)
    return secret_dict['openai_api_key']
