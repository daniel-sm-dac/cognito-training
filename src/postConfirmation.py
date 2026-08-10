"""
Cognito Post Confirmation trigger.

Fires once, right after the user successfully enters the OTP code
(triggerSource == "PostConfirmation_ConfirmSignUp"). This is the right
place to create the DynamoDB extension row, since we now know the user
is a real, verified account and event["request"]["userAttributes"]["sub"]
is stable and permanent.

It can also fire for PostConfirmation_ConfirmForgotPassword - guard
against that so we don't overwrite an existing profile on a password reset.
"""
import logging
import time
from botocore.exceptions import ClientError
from src import db

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info("PostConfirmation event: %s", event)

    if event["triggerSource"] != "PostConfirmation_ConfirmSignUp":
        # e.g. PostConfirmation_ConfirmForgotPassword - nothing to do
        return event

    attributes = event["request"]["userAttributes"]
    user_id = attributes["sub"]
    email = attributes.get("email", "")
    givenName = attributes.get("givenName", "")
    familyName = attributes.get("familyName", "")

    table = db.getTable()
    try:
        table.put_item(
            Item={
                "userId": user_id,
                "email": email,
                "givenName": givenName,
                "familyName": familyName,
                "status": "CONFIRMED",
                "signUpTimestamp": int(time.time()),
                "lastLoginTimestamp": None,
                "loginCount": 0,
            },
            # Guard against double-writes if Cognito retries the trigger
            ConditionExpression="attribute_not_exists(userId)",
        )
    except ClientError as err:
        if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
            # Profile already exists (e.g. Cognito retried the trigger).
            # Don't fail the confirmation over this - the user is still
            # legitimately confirmed in Cognito.
            logger.info("Profile for %s already exists, skipping insert", user_id)
        else:
            raise

    return event