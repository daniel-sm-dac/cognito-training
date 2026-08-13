from datetime import datetime, timezone
from src import db

def handler(event, context):
    # user_id = event['userName']
    user_id = event["request"]["userAttributes"]["sub"]

    now = datetime.now(timezone.utc).isoformat()

    db.update_profile(user_id, {"verified": True, "verified_at": now})

    return event