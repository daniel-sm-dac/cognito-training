import json
import boto3
import db

cognito = boto3.client("cognito-idp")

USER_POOL_CLIENT_ID = "your-client-id"


def handler(event, context):
  body = json.loads(event["body"])
  username = body["username"]
  password = body["password"]
  registration_channel = body.get("registration_channel", "unknown")

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

  table = db.getTable()
  db.create_session(table, user_id, id_token, access_token, refresh_token, registration_channel)

  return {
    "statusCode": 200,
    "headers": {"Access-Control-Allow-Origin": "*"},
    "body": json.dumps({
      "user_id": user_id,
      "id_token": id_token,
      "access_token": access_token,
      "refresh_token": refresh_token,
    }),
  }