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