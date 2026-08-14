import json
from src import db

def handler(event, context):
	user_id = event["pathParameter"]["userId"]

	session = db.get_session(user_id)

	if not session or session.get("refresh_status") != "valid":
		response = {
			"statusCode" : 404,
			"headers" : {"Access-Control-Allow-Origin" : "*"},
			"body" : json.dumps({"error" : "No valid session found"}),
		}
		return response

	reponse = {
		"statusCode": 200,
		"headers": {"Access-Control-Allow-Origin": "*"},
		"body": json.dumps(session["token_set"]),
	}

	return response