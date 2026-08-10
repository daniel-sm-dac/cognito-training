"""
Cognito Post Authentication trigger.

Fires right after Cognito issues tokens for a successful signIn(). This is
where we track authentication activity in the DynamoDB extension table -
updating lastLoginTimestamp and incrementing loginCount without touching
anything Cognito itself owns (password, tokens, MFA state, etc).
"""
import logging
import time
from src import db

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    table = db.getTable()
    logger.info("PostAuthentication event: %s", event)

    user_id = event["request"]["userAttributes"]["sub"]

    table.update_item(
        Key={"userId": user_id},
        UpdateExpression=(
            "SET lastLoginTimestamp = :now "
            "ADD loginCount :increment"
        ),
        ExpressionAttributeValues={
            ":now": int(time.time()),
            ":increment": 1,
        },
    )

    print ("Authentication successful")
    print ("Trigger function =", event['triggerSource'])
    print ("User pool = ", event['userPoolId'])
    print ("App client ID = ", event['callerContext']['clientId'])
    print ("User ID = ", event['userName'])

    return event