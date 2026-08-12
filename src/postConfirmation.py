from datetime import datetime, timezone
from src import db

def handler(event, context):
    table = db.getTable()

    user_id = event['userName']
    now = datetime.now(timezone.utc).isoformat()

    table.update_item(
        Key={'userId': user_id},
        UpdateExpression='SET verified = :v, verifiedAt = :va, updatedAt = :ua',
        ExpressionAttributeValues={
            ':v': True,
            ':va': now,
            ':ua': now,
        }
    )

    return event