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

# Function to get Trello lists
def get_trello_lists():
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN
    }
    logging.debug(f"Getting Trello lists with URL: {url} and query: {query}")
    response = requests.get(url, params=query)
    response.raise_for_status()
    return response.json()

# Function to get Trello tasks
def get_trello_tasks():
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN
    }
    logging.debug(f"Getting Trello tasks with URL: {url} and query: {query}")
    response = requests.get(url, params=query)
    response.raise_for_status()
    return response.json()

# Function to create a task in Trello
def create_trello_task(task):
    lists = get_trello_lists()
    list_id = None
    for lst in lists:
        if lst['name'] == TRELLO_LIST_NAME:
            list_id = lst['id']
            break
    
    if not list_id:
        logging.error(f"List named '{TRELLO_LIST_NAME}' not found in Trello board.")
        return
    
    url = f"https://api.trello.com/1/cards"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN
    }
    data = {
        'name': task['name'],
        'desc': task['description'],
        'idList': list_id
    }
    logging.debug(f"Creating new Trello task with data: {data}")
    response = requests.post(url, params=query, json=data)
    response.raise_for_status()
    return response.json()

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

# Function to sync Motion tasks to Trello
def sync_motion_to_trello():
    motion_tasks = get_motion_tasks()
    trello_tasks = get_trello_tasks()

    existing_trello_tasks = {card['name']: card for card in trello_tasks}

    for motion_task in motion_tasks:
        if motion_task['name'] not in existing_trello_tasks:
            logging.info(f"Creating new Trello task for Motion task '{motion_task['name']}'")
            create_trello_task(motion_task)
        else:
            logging.info(f"Trello task already exists for Motion task '{motion_task['name']}'")

# Run the sync process
if __name__ == "__main__":
    sync_motion_to_trello()