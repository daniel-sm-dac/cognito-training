from datetime import datetime, timezone
from src import db
import uuid

def handler(event, context):
    table = db.getTable()

    user_id = event['userName']
    now = datetime.now(timezone.utc).isoformat()
    session_id = str(uuid.uuid4())

    table.update_item(
        Key={'userId': user_id},
        UpdateExpression=(
            'SET lastSignIn = :ls, tokenIssuedAt = :ti, updatedAt = :ua, '
            'sessionToken = :st'
        ),
        ExpressionAttributeValues={
            ':ls': now,
            ':ti': now,
            ':ua': now,
            ':st': session_id,
        }
    )

    return event