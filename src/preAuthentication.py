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

    user_id = event["request"]["userAttributes"]["sub"]
    logger.info("PreAuthentication for user_id: %s", user_id)
    logger.debug("PreAuthentication event: %s", event)

    response = table.get_item(Key={"userId": user_id})
    profile = response.get("Item")

    if profile and profile.get("status") == "SUSPENDED":
        logger.info("Blocked sign-in for suspended user_id: %s", user_id)
        raise Exception("This account has been suspended. Contact support.")

    return event