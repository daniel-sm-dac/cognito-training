import json
import os
import boto3
import time
from botocore.exceptions import ClientError
from src import db


cognito = boto3.client('cognito-idp', region_name=os.environ['REGION'])
USER_POOL_CLIENT_ID = os.environ['COGNITO_CLIENT_ID']

def handler(event, context):
  # Get the stored refresh token (which user/app session this is for)
  body = json.loads(event["body"])
  refresh_token = body.get('refresh_token')
  user_id = body.get("user_id")
  client_app_id = body.get("client_app_id")

  if not refresh_token or not user_id:
    response = {
      'statusCode': 400,
      "headers": {"Access-Control-Allow-Origin": "*"},
      'body': json.dumps({'error': 'refreshToken and userId are required'})
    }
    return response

  # Get session to check if the refresh status is valid; if not session is expired
  session = db.get_session(user_id, client_app_id)
  if not session or session.get("refresh_status") != "valid":
    response = {
      'statusCode': 400,
      "headers": {"Access-Control-Allow-Origin": "*"},
      'body': json.dumps({'error': 'session_expired'})
    }
    return response
  
  # Exchange the refresh token for a new ID/access token pair
  try:
    result = cognito.initiate_auth(
      ClientId=USER_POOL_CLIENT_ID,
      AuthFlow='REFRESH_TOKEN_AUTH',
      AuthParameters={'REFRESH_TOKEN': refresh_token}
    )
  except ClientError as e:
    # refresh token expired, revoked, or invalid — session is truly over (user must log in again)
    db.force_expire_session(user_id, client_app_id)
    return {
      'statusCode': 401,
      "headers": {"Access-Control-Allow-Origin": "*"},
      'body': json.dumps({'error': str(e)})
    }

  auth_result = result['AuthenticationResult']
  new_id_token = auth_result['IdToken']
  new_access_token = auth_result['AccessToken']

  # Save the new tokens to DynamoDB (refresh_token stays the same)
  db.refresh_session(user_id, client_app_id, new_id_token, new_access_token)

  response = {
    'statusCode' : 200,
    "headers": {"Access-Control-Allow-Origin": "*"},
    'body': json.dumps({
      'id_token': new_id_token,
      'access_token': new_access_token,
    })
  }

  return response