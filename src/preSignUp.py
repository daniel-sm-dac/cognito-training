import logging
from datetime import datetime, timezone
from src import db

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):

  # logger.info("PreSignUp event: %s", event)

  # attributes = event["request"]["userAttributes"]
  # given_name = attributes.get("given_name", "").strip()
  # family_name = attributes.get("family_name", "").strip()

  # if not given_name:
  #     raise Exception("Given name is required.")
  # if not family_name:
  #     raise Exception("Family name is required.")
  
  table = db.getTable()
  
  user_attributes = event['request']['userAttributes']
  user_id = event['userName']

  now = datetime.now(timezone.utc).isoformat()

  table.put_item(
    Item={
      'userId': user_id,
      'email': user_attributes.get('email'),
      'givenName': user_attributes.get('given_name'),
      'familyName': user_attributes.get('family_name'),
      'verified': False,
      'createdAt': now,
      'updatedAt': now,
    },
    ConditionExpression='attribute_not_exists(userId)' # avoid overwriting on retry
  )

  return event
