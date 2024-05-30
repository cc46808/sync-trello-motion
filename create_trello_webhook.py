import os
import requests
import json

# Fetching environment variables
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
CALLBACK_URL = os.getenv('CALLBACK_URL')

def create_trello_webhook(callback_url, id_model, api_key, api_token):
    url = "https://api.trello.com/1/webhooks/"

    headers = {
        "Accept": "application/json"
    }

    query = {
        'callbackURL': callback_url,
        'idModel': id_model,
        'key': api_key,
        'token': api_token
    }

    response = requests.request(
        "POST",
        url,
        headers=headers,
        params=query
    )

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        print(f"Response Text: {response.text}")
        return None
    
    return json.loads(response.text)

webhook_response = create_trello_webhook(CALLBACK_URL, TRELLO_BOARD_ID, TRELLO_API_KEY, TRELLO_API_TOKEN)
print(json.dumps(webhook_response, sort_keys=True, indent=4, separators=(",", ": ")))