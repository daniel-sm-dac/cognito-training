from src import db

def handler(event, context):
    table = db.getTable()

    user_id = event['userName']

    response = table.get_item(Key={'userId': user_id})
    item = response.get('Item', {})

    event['response']['claimsAndScopeOverrideDetails'] = {
        'idTokenGeneration': {
            'claimsToAddOrOverride': {
                'role': item.get('role', 'user'),
                'verified': str(item.get('verified', False)),
            }
        }
    }

    return event