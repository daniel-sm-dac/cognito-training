import logging
from datetime import datetime, timezone
from src import db
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
  
  table = db.getTable()
  
  user_attributes = event['request']['userAttributes']
  logger.info("user_attributes: %s", user_attributes)

  user_id = event['userName']
  email = user_attributes.get('email')

  logger.info("PreSignUp for email: %s", email)

  existing = table.query(
      IndexName="email-index",
      KeyConditionExpression=Key("email").eq(email)
  ).get("Items")

  if existing:
    logger.info("An account with this email already exists: %s", email)
    raise Exception("An account with this email already exists")
  

  now = datetime.now(timezone.utc).isoformat()

  table.put_item(
    Item={
      'userId': user_id,
      'email': email,
      'givenName': user_attributes.get('given_name'),
      'familyName': user_attributes.get('family_name'),
      'verified': False,
      'role': 'user',
      'status': 'ACTIVE',
      'createdAt': now,
      'updatedAt': now,
      'session': ''
    },
    ConditionExpression='attribute_not_exists(userId)'  # race-condition safety net for userId
  )

  return event



