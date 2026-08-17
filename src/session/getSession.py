import json
from src import db
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
	user_id = event["pathParameters"]["userId"]
	client_app_id = event["pathParameters"]["client_app_id"]

	session = db.get_session(user_id, client_app_id)
	logger.info(json.dumps(session["token_set"]))

	if not session or session.get("refresh_status") != "valid":
		response = {
			"statusCode" : 404,
			"headers" : {"Access-Control-Allow-Origin" : "*"},
			"body" : json.dumps({"error" : "no_session_found"}),
		}
		return response

	response = {
		"statusCode": 200,
		"headers": {"Access-Control-Allow-Origin": "*"},
		"body": json.dumps(session["token_set"]),
	}

	return response