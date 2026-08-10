import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info("PreSignUp event: %s", event)
 
    attributes = event["request"]["userAttributes"]
    given_name = attributes.get("given_name", "").strip()
    family_name = attributes.get("family_name", "").strip()
 
    if not given_name:
        raise Exception("Given name is required.")
    if not family_name:
        raise Exception("Family name is required.")
 
    return event
