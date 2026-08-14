import json
from src import db

def handler(event, context):
  body = json.loads(event["body"])
  user_id = body["userId"]
  id_token = body["idToken"]
  acces_token = body["accessToken"]
  refresh_token = body["refreshToken"]
  refresh_token = body.get("registrationChannel", "unknow-app")

  db.create_session(user_id, id_token, acces_token, refresh_token, refresh_token)

  response = {
    "statusCode": 200,
    "headers": {"Access-Control-Allow-Origin": "*"},
    "body": json.dumps({"status": "session created"}),
  }

  return response