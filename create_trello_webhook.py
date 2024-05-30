import os
import requests

TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
CALLBACK_URL = os.getenv('CALLBACK_URL')

def create_trello_webhook(callback_url, id_model, description="Trello Webhook"):
    url = f"https://api.trello.com/1/tokens/{TRELLO_API_TOKEN}/webhooks/"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'callbackURL': callback_url,
        'idModel': id_model,
        'description': description
    }
    
    # Print the URL and parameters for debugging
    print(f"URL: {url}")
    print(f"Parameters: {query}")
    
    response = requests.post(url, params=query)
    response.raise_for_status()
    return response.json()

webhook_response = create_trello_webhook(CALLBACK_URL, TRELLO_BOARD_ID)
print(webhook_response)
