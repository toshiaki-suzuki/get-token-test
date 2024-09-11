import json
import boto3
import os
from botocore.exceptions import ClientError

def lambda_handler(event, context):

    print(event)

    # POSTリクエストボディからuser_idを取得
    try:
        user_id = event["user_id"]
    except (KeyError, json.JSONDecodeError):
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid request body or missing user_id')
        }

    # user_idの検証（必要に応じて実装）
    if not validate_user_id(user_id):
        return {
            'statusCode': 403,
            'body': json.dumps('Invalid user_id')
        }

    # S3アクセス用の一時的なクレデンシャルを生成
    sts_client = boto3.client('sts')
    try:
        response = sts_client.assume_role(
            RoleArn=os.environ['S3_ROLE_ARN'],
            RoleSessionName=f'S3AccessSession-{user_id}',
            DurationSeconds=3600  # 1時間有効
        )

        credentials = response['Credentials']

        return {
            'statusCode': 200,
            'body': json.dumps({
                'AccessKeyId': credentials['AccessKeyId'],
                'SecretAccessKey': credentials['SecretAccessKey'],
                'SessionToken': credentials['SessionToken'],
                'Expiration': credentials['Expiration'].isoformat()
            })
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def validate_user_id(user_id):
    # user_idの検証ロジックをここに実装
    # 例: データベースでuser_idの存在確認など
    return True  # 仮の実装
