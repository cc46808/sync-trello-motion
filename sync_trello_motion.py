import requests
import os
import time

# Motion API credentials
MOTION_API_KEY = os.getenv('MOTION_API_KEY')
MOTION_WORKSPACE_ID = os.getenv('MOTION_WORKSPACE_ID')

# Trello API credentials
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')

# Motion API base URL
MOTION_BASE_URL = 'https://api.usemotion.com'

# Trello API base URL
TRELLO_BASE_URL = 'https://api.trello.com/1'

# Headers for Motion API
headers_motion = {
    'Authorization': f'Bearer {MOTION_API_KEY}',
    'Content-Type': 'application/json'
}

def get_motion_tasks():
    url = f'{MOTION_BASE_URL}/tasks'
    params = {'workspaceId': MOTION_WORKSPACE_ID}
    response = requests.get(url, headers=headers_motion, params=params)
    try:
        response.raise_for_status()
        return response.json().get('tasks', [])
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
    except ValueError:
        print(f'Error decoding JSON response: {response.text}')
    return []

def get_trello_cards():
    url = f'{TRELLO_BASE_URL}/boards/{TRELLO_BOARD_ID}/cards'
    params = {'key': TRELLO_API_KEY, 'token': TRELLO_API_TOKEN}
    response = requests.get(url, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
    except ValueError:
        print(f'Error decoding JSON response: {response.text}')
    return []

def create_motion_task(name, description):
    url = f'{MOTION_BASE_URL}/tasks'
    data = {
        'name': name,
        'workspaceId': MOTION_WORKSPACE_ID,
        'description': description,
        'priority': 'MEDIUM'
    }
    response = requests.post(url, headers=headers_motion, json=data)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
    except ValueError:
        print(f'Error decoding JSON response: {response.text}')
    return None

def create_trello_card(name, description):
    url = f'{TRELLO_BASE_URL}/cards'
    data = {
        'name': name,
        'desc': description,
        'idList': TRELLO_BOARD_ID,
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN
    }
    response = requests.post(url, data=data)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
    except ValueError:
        print(f'Error decoding JSON response: {response.text}')
    return None

def update_motion_task_status(task_id, completed):
    url = f'{MOTION_BASE_URL}/tasks/{task_id}'
    data = {'completed': completed}
    response = requests.patch(url, headers=headers_motion, json=data)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
    except ValueError:
        print(f'Error decoding JSON response: {response.text}')
    return None

def update_trello_card_status(card_id, completed):
    url = f'{TRELLO_BASE_URL}/cards/{card_id}'
    data = {'closed': completed}
    params = {'key': TRELLO_API_KEY, 'token': TRELLO_API_TOKEN}
    response = requests.put(url, data=data, params=params)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
    except ValueError:
        print(f'Error decoding JSON response: {response.text}')
    return None

def sync_to_trello():
    motion_tasks = get_motion_tasks()
    trello_cards = get_trello_cards()

    # Add Motion tasks to Trello if not already present
    for task in motion_tasks:
        if not any(card['name'] == task['name'] for card in trello_cards):
            create_trello_card(task['name'], task['description'])
        else:
            for card in trello_cards:
                if card['name'] == task['name']:
                    if task['completed'] and not card['closed']:
                        update_trello_card_status(card['id'], True)
                    elif not task['completed'] and card['closed']:
                        update_motion_task_status(task['id'], True)

def sync_to_motion():
    trello_cards = get_trello_cards()
    motion_tasks = get_motion_tasks()

    # Add Trello cards to Motion if not already present
    for card in trello_cards:
        if not any(task['name'] == card['name'] for task in motion_tasks):
            create_motion_task(card['name'], card['desc'])
        else:
            for task in motion_tasks:
                if task['name'] == card['name']:
                    if card['closed'] and not task['completed']:
                        update_motion_task_status(task['id'], True)
                    elif not card['closed'] and task['completed']:
                        update_trello_card_status(card['id'], True)

def two_way_sync():
    sync_to_trello()
    sync_to_motion()

if __name__ == "__main__":
    two_way_sync()
