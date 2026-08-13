import logging
import json
from src import db

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
  claims = event["requestContext"]["authorizer"]["claims"]
  logger.info("check all claims: %s", claims)
  
  role = claims.get("custom:role")

  logger.info("check role: %s", role)


  if role != "user":
    logger.info("check role inside the condition: %s", role)
    response = {
      "statusCode": 403,
      "body": json.dumps({"error": "Forbidden — not authorize"}),
    }
    return response

  table = db.getTable()
  table_response = table.scan()
  users = table_response.get('Items', [])

  response = {
    'statusCode' : 200,
    'headers': {
        "Access-Control-Allow-Origin": "*",
    },
    'body' : json.dumps({
        'users' : users,
        'count' : len(users)
    })
  }

  return response