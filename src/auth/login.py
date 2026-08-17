import json
import boto3
from src import db
import logging
import os

cognito = boto3.client("cognito-idp")
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
  try:
    body = json.loads(event["body"])
    username = body["username"]
    password = body["password"]
    client_app_id = body["client_app_id"]
    USER_POOL_CLIENT_ID = os.environ['COGNITO_CLIENT_ID']

    try:
      auth_result = cognito.initiate_auth(
        ClientId=USER_POOL_CLIENT_ID,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
      )
    except cognito.exceptions.NotAuthorizedException:
      return {
        "statusCode": 401,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({"error": "invalid_credentials"}),
      }

    id_token = auth_result["AuthenticationResult"]["IdToken"]
    access_token = auth_result["AuthenticationResult"]["AccessToken"]
    refresh_token = auth_result["AuthenticationResult"]["RefreshToken"]

    user_resp = cognito.get_user(AccessToken=access_token)
    user_id = next(a["Value"] for a in user_resp["UserAttributes"] if a["Name"] == "sub")

    db.create_session(user_id, client_app_id, id_token, access_token, refresh_token, client_app_id)

    response = {
      "statusCode": 200,
      "headers": {"Access-Control-Allow-Origin": "*"},
      "body": json.dumps({
        "user_id": user_id,
        "id_token": id_token,
        "access_token": access_token,
        "refresh_token": refresh_token,
      }),
    }

    logger.info(json.dumps(response))
    return response

  except Exception as e:
    logger.error(f"login handler failed: {e}", exc_info=True)
    return {
      "statusCode": 500,
      "headers": {"Access-Control-Allow-Origin": "*"},
      "body": json.dumps({"error": "internal_error", "message": str(e)}),
    }