import logging
from src import db

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    
    user_id = event['userName']
    logger.info("PreAuthentication for user_id: %s", user_id)

    profile = db.get_profile(user_id)

    if profile and profile.get("status") == "SUSPENDED":
        logger.info("Blocked sign-in for suspended user_id: %s", user_id)
        raise Exception("This account has been suspended. Contact support.")

    return event