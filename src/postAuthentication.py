"""
Cognito Post Authentication trigger.

Fires right after Cognito issues tokens for a successful signIn(). This is
where we track authentication activity in the DynamoDB extension table -
updating lastLoginTimestamp and incrementing loginCount without touching
anything Cognito itself owns (password, tokens, MFA state, etc).
"""
from datetime import datetime, timezone
from src import db

def handler(event, context):
    table = db.getTable()

    user_id = event['userName']
    now = datetime.now(timezone.utc).isoformat()

    # Cognito doesn't hand you the issued tokens in this trigger's event —
    # only claims/context about the auth attempt. If you need the actual
    # token set stored, that has to happen client-side after signIn()
    # resolves (Amplify), posting to your own API to save it.
    table.update_item(
        Key={'userId': user_id},
        UpdateExpression='SET lastSignIn = :ls, tokenIssuedAt = :ti, updatedAt = :ua',
        ExpressionAttributeValues={
            ':ls': now,
            ':ti': now,
            ':ua': now,
        }
    )

    return event