import logging
from datetime import datetime, timezone
from src import db
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
  
  user_id = event['userName']
  email = event["request"]["userAttributes"]["email"]

  logger.info("user_attributes: %s", event["request"]["userAttributes"])
  logger.info("PreSignUp for email: %s", email)

  # existing = table.query(
  #     IndexName="email-index",
  #     KeyConditionExpression=Key("email").eq(email)
  # ).get("Items")

  if db.email_exists(email):
    logger.info("An account with this email already exists: %s", email)
    raise Exception("An account with this email already exists")

  try:
    now = datetime.now(timezone.utc).isoformat()
    db.put_profile({
      'user_id': user_id,
      'email': email,
      'given_name': event["request"]["userAttributes"].get('given_name'),
      'family_name': event["request"]["userAttributes"].get('family_name'),
      'verified': False,
      'role': 'user',
      'status': 'ACTIVE',
      'created_at': now,
      'updated_at': now,
    })

  except ClientError as e:
    if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
      raise Exception("User already exists")
    raise

  return event



