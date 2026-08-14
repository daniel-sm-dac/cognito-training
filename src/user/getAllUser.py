import json
import logging
from decimal import Decimal
from src import db

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _decimal_default(obj):
  if isinstance(obj, Decimal):
    return int(obj) if obj % 1 == 0 else float(obj)
  raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


def handler(event, context):
  claims = event["requestContext"]["authorizer"]["claims"]
  role = claims.get("custom:role")

  if role != "user":
    return {
      "statusCode": 403,
      "headers": {"Access-Control-Allow-Origin": "*"},
      "body": json.dumps({"error": "Forbidden — not authorized"}),
    }

  table = db.getTable()
  table_response = table.scan()
  users = table_response.get("Items", [])

  return {
    "statusCode": 200,
    "headers": {"Access-Control-Allow-Origin": "*"},
    "body": json.dumps(
      {"users": users, "count": len(users)},
      default=_decimal_default,
    ),
  }