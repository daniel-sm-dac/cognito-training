from src import db

def handler(event, context):
    table = db.getTable()
    user_id = event['userName']
    response = table.get_item(Key={'userId': user_id})
    profile = response.get("Item", {})

    event['response']['claimsAndScopeOverrideDetails'] = {
        'idTokenGeneration': {
            'claimsToAddOrOverride': {
                'custom:role': profile.get("role", "user"),
                'custom:verified': str(profile.get('verified', False)),
            }
        }
    }

    return event