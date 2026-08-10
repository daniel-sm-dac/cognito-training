"""
Cognito Pre Authentication trigger.

Fires after signIn() is called but before Cognito checks the password.
Cognito already rejects unconfirmed users and disabled users on its own
(UserNotConfirmedException / NotAuthorizedException), so this trigger is
mostly a hook for your own extra checks against the DynamoDB profile -
e.g. an account you've flagged for manual review or suspended outside
of Cognito's own Enabled/Disabled flag.

Raising an exception here blocks the sign-in attempt entirely and the
message becomes the error surfaced to Amplify's signIn() call.
"""
import logging
from src import db

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    table = db.getTable()
    logger.info("PreAuthentication event: %s", event)

    user_id = event["request"]["userAttributes"]["sub"]
    
    response = table.get_item(Key={"userId": user_id})
    profile = response.get("Item")

    if profile and profile.get("status") == "SUSPENDED":
        raise Exception("This account has been suspended. Contact support.")

    return event