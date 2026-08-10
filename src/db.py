import boto3, os

def getTable():
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(os.environ['USER_PROFILE_TABLE'])