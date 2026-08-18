import boto3, os
import time
from boto3.dynamodb.conditions import Key
import uuid
from datetime import datetime, timezone

def get_profile(user_id):
  table = getTable()
  response = table.get_item(Key={"user_id": user_id, "SK": "user"})
  return response.get("Item")

def put_profile(item):
  # Item must include user_id + SK='PROFILE' already set by the caller.
  table = getTable()
  item["SK"] = "user"
  table.put_item(Item=item, ConditionExpression="attribute_not_exists(user_id)")

def email_exists(email):
  # check if email exist in the dynamoDB
  table = getTable()
  response = table.query(
    IndexName="email-index",
    KeyConditionExpression=Key("email").eq(email)
  )
  return len(response["Items"]) > 0

def update_profile(user_id, fields: dict):
  table = getTable()
  fields["updated_at"] = datetime.now(timezone.utc).isoformat()
  table.update_item(
    Key={"user_id": user_id, "SK": "user"},
    UpdateExpression="SET " + ", ".join(f"{k} = :{k}" for k in fields),
    ExpressionAttributeValues={f":{k}": v for k, v in fields.items()}
  )

def get_session(user_id, client_app_id):
  table = getTable()
  response = table.get_item(Key={"user_id": user_id, "SK": f"session#{client_app_id}"})
  return response.get("Item")

def create_session(user_id, client_app_id, id_token, access_token, refresh_token, registration_channel):
  table = getTable()
  now = datetime.now(timezone.utc).isoformat()
  response = table.put_item(Item={
    "user_id": user_id,
    "SK": f"session#{client_app_id}",
    "token_set": {
        "id_token": id_token,
        "access_token": access_token,
        "refresh_token": refresh_token
    },
    "registration_channel": registration_channel,
    "refresh_status": "valid",
    "created_at": now,
    "updated_at": now,
  })

  return response

def refresh_session(user_id, client_app_id, id_token, access_token):
  table = getTable()
  # Called after using the stored refreshToken to mint a fresh id/access token.
  # refreshToken itself doesnt change on a standard refresh, so it's left as-is.
  now = datetime.now(timezone.utc).isoformat()
  table.update_item(
    Key={
      "user_id": user_id,
      "SK": f"session#{client_app_id}"
    },
    UpdateExpression="SET token_set.id_token = :i, token_set.access_token = :a, refresh_status = :s, updated_at = :u",
    ExpressionAttributeValues={
      ":i": id_token,
      ":a": access_token,
      ":s": "valid",
      ":u": now,
    }
  )

def force_expire_session(user_id, client_app_id):
  table = getTable()
  now = datetime.now(timezone.utc).isoformat()
  table.update_item(
    Key={"user_id": user_id, "SK": f"session#{client_app_id}"},
    UpdateExpression="SET refresh_status = :s, updated_at = :u",
    ExpressionAttributeValues={":s": "expired", ":u":now}
  )

def getTable():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(os.environ['TABLE_NAME'])