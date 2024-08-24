import requests
import json
import boto3
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数から設定を読み込む
API_ENDPOINT = os.getenv('API_ENDPOINT')
API_KEY = os.getenv('API_KEY')
TOKEN_FILE = os.getenv('TOKEN_FILE')


def get_token(user_id):
    """APIを呼び出してトークンを取得する"""
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "user_id": user_id
    }
    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    if response.status_code == 200:
        res = json.loads(response.text)
        credentials = json.loads(res['body'])
        # 有効期限を追加（1時間とする）
        credentials['Expiration'] = (
            datetime.now() + timedelta(hours=1)).isoformat()
        save_token(credentials)
        return credentials
    else:
        raise Exception(f"Failed to get token: {response.text}")


def save_token(credentials):
    """トークンをファイルに保存する"""
    with open(TOKEN_FILE, 'w') as f:
        json.dump(credentials, f)


def load_token():
    """保存されたトークンを読み込む"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None


def is_token_valid(credentials):
    """トークンが有効かどうかを確認する"""
    if credentials is None:
        return False
    expiration = datetime.fromisoformat(credentials['Expiration'])
    return datetime.now() < expiration


def get_valid_credentials(user_id):
    """有効なクレデンシャルを取得する"""
    credentials = load_token()
    if not is_token_valid(credentials):
        print("Token expired or not found. Getting a new one.")
        credentials = get_token(user_id)
    else:
        print("Using cached token.")
    return credentials


def create_s3_client(credentials):
    """取得したクレデンシャルを使用してS3クライアントを作成する"""
    return boto3.client('s3',
                        aws_access_key_id=credentials['AccessKeyId'],
                        aws_secret_access_key=credentials['SecretAccessKey'],
                        aws_session_token=credentials['SessionToken']
                        )


def list_buckets(s3_client):
    """S3バケットの一覧を取得する"""
    response = s3_client.list_buckets()
    print("S3 Buckets:")
    for bucket in response['Buckets']:
        print(f"- {bucket['Name']}")


def main():
    user_id = "example_user_id"  # 実際のuser_idに置き換えてください
    try:
        # 有効なクレデンシャルを取得
        credentials = get_valid_credentials(user_id)
        print("Successfully obtained valid credentials")

        # S3クライアントの作成
        s3_client = create_s3_client(credentials)

        # S3バケットの一覧表示
        list_buckets(s3_client)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
