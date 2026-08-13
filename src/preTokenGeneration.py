from src import db

def handler(event, context):
  user_id = event['userName']
  profile = db.get_profile(user_id)

  event['response']['claimsAndScopeOverrideDetails'] = {
    'idTokenGeneration': {
      'claimsToAddOrOverride': {
        'custom:role': profile.get("role", "user"),
        'custom:verified': str(profile.get('verified', False)),
      }
    }
  }

  return event