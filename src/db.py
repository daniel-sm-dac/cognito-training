import boto3, os
import time
from boto3.dynamodb.conditions import Key
import uuid
from datetime import datetime, timezone

def get_profile(user_id):
  table = getTable()
  response = table.get_item(Key={"userId": user_id})
  return response.get("Item")

def put_profile(item):
  # Item must include user_id + SK='PROFILE' already set by the caller.
  table = getTable()
  table.put_item(Item=item, ConditionExpression="attribute_not_exists(userId)")

def email_exists(email):
  # check if email exist in the dynamoDB
  table = getTable()
  response = table.query(
    IndexName="email-index",
    KeyConditionExpression=Key("email").eq(email)
  )
  return len(response["Items"]) > 0

def update_profile(table, user_id, fields: dict):
  fields["updatedAt"] = int(time.time())
  table.update_item(
      Key={"userId": user_id},
      UpdateExpression="SET " + ", ".join(f"{k} = :{k}" for k in fields),
      ExpressionAttributeValues={f":{k}": v for k, v in fields.items()}
  )

# def create_session(user_id, client_app_id, ttl_seconds=8 * 60 * 60):
#     #New — writes a SESSION item, separate from PROFILE, under the same userId PK.
#     table = getTable()
#     session_token = str(uuid.uuid4())
#     now = int(time.time())
#     table.put_item(Item={
#         "userId": user_id,                  # PK
#         "SK": f"SESSION#{session_token}",   # SK — distinguishes from PROFILE item
#         "lookupKey": session_token,         # GSI PK — validate-session looks up by this
#         "itemType": "SESSION",
#         "clientAppId": client_app_id,
#         "createdAt": now,
#         "expiresAt": now + ttl_seconds,     # DynamoDB TTL attribute (epoch seconds)
#         "lastValidatedAt": now,
#         "status": "active",
#     })
#     return session_token


def getTable():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(os.environ['TABLE_NAME'])