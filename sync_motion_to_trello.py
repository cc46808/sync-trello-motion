import os
import requests
import json
import http.client
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Trello API credentials from environment variables
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
TRELLO_LIST_NAME = os.getenv('TRELLO_LIST_NAME')

# Motion API credentials from environment variables
MOTION_API_KEY = os.getenv('MOTION_API_KEY')
MOTION_API_HOST = 'api.usemotion.com'
MOTION_WORKSPACE_ID = os.getenv('MOTION_WORKSPACE_ID')

# Function to get Motion tasks
def get_motion_tasks():
    conn = http.client.HTTPSConnection(MOTION_API_HOST)
    headers = {
        'Accept': "application/json",
        'X-API-Key': MOTION_API_KEY
    }
    conn.request("GET", "/v1/tasks", headers=headers)
    res = conn.getresponse()
    data = res.read()
    tasks_response = json.loads(data.decode("utf-8"))
    conn.close()
    return tasks_response['tasks']

# Function to get Trello lists
def get_trello_lists():
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN
    }
    response = requests.get(url, params=query)
    response.raise_for_status()
    return response.json()

# Function to create a task in Trello
def create_trello_task(task, list_id):
    url = f"https://api.trello.com/1/cards"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'idList': list_id,
        'name': task['name'],
        'desc': task.get('description', ''),
        'due': task.get('dueDate')
    }
    response = requests.post(url, params=query)
    response.raise_for_status()
    return response.json()

# Function to update a task in Trello
def update_trello_task(card_id, task):
    url = f"https://api.trello.com/1/cards/{card_id}"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'name': task['name'],
        'desc': task.get('description', ''),
        'due': task.get('dueDate')
    }
    response = requests.put(url, params=query)
    response.raise_for_status()
    return response.json()

# Function to sync Motion tasks to Trello
def sync_motion_to_trello():
    motion_tasks = get_motion_tasks()
    trello_lists = get_trello_lists()
    
    # Find the target list in Trello
    target_list_id = None
    for trello_list in trello_lists:
        if trello_list['name'] == TRELLO_LIST_NAME:
            target_list_id = trello_list['id']
            break
    
    if not target_list_id:
        logging.error(f"Target list '{TRELLO_LIST_NAME}' not found in Trello board '{TRELLO_BOARD_ID}'")
        return

    # Get existing Trello cards
    existing_trello_tasks = {card['name']: card for card in get_trello_tasks()}
    
    for task in motion_tasks:
        if task['name'] in existing_trello_tasks:
            # Update existing Trello task
            update_trello_task(existing_trello_tasks[task['name']]['id'], task)
            logging.info(f"Updated Trello task for Motion task '{task['name']}'")
        else:
            # Create new Trello task
            create_trello_task(task, target_list_id)
            logging.info(f"Created new Trello task for Motion task '{task['name']}'")

if __name__ == "__main__":
    sync_motion_to_trello()
