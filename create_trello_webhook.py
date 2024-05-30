import os
import requests

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
CALLBACK_URL = os.getenv('CALLBACK_URL')

def create_trello_webhook(callback_url, id_model, description="Trello Webhook"):
    url = "https://api.trello.com/1/webhooks/"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN
    }
    data = {
        'callbackURL': callback_url,
        'idModel': id_model,
        'description': description
    }

    print(f"URL: {url}")
    print(f"Query Params: {query}")
    print(f"Data: {data}")

    response = requests.post(url, params=query, json=data)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        print(f"Response Text: {response.text}")
        return None
    return response.json()

webhook_response = create_trello_webhook(CALLBACK_URL, TRELLO_BOARD_ID)
print(webhook_response)
