import requests
import os

# Trello API credentials
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_BOARD_ID = '66562f7fa2328cbe53e2f0e0'  # Board ID for "CC: To Do"

def get_trello_cards(board_id):
    url = f"https://api.trello.com/1/boards/{board_id}/cards"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN
    }

    response = requests.get(url, params=query)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    cards = get_trello_cards(TRELLO_BOARD_ID)
    for card in cards:
        print(f"Card Name: {card['name']}, Card ID: {card['id']}")