# Does not need anymore after the refactoring
import json
import logging
from src import db

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
  body = json.loads(event["body"])
  user_id = body.get("user_id")
  id_token = body.get("id_token")
  access_token = body.get("access_token")
  refresh_token = body.get("refresh_token")
  registration_channel = body.get("registration_channel", "unknown")

  logger.debug(body)

  dbResponse = db.create_session(user_id, id_token, access_token, refresh_token, registration_channel)
  logger.debug("DB Response: %s", dbResponse)

  response = {
    "statusCode": 200,
    "headers": {"Access-Control-Allow-Origin": "*"},
    "body": json.dumps({"status": "session created"}),
  }

  return response