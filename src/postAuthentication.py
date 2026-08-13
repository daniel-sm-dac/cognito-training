from datetime import datetime, timezone
from src import db
import uuid

def handler(event, context):
    user_id = event["userName"]
    now = datetime.now(timezone.utc).isoformat()
    db.update_profile(user_id, {"last_sign_in": now})

    return event