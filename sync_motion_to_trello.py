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

# Motion API credentials from environment variables
MOTION_API_KEY = os.getenv('MOTION_API_KEY')
MOTION_API_HOST = 'api.usemotion.com'
MOTION_WORKSPACE_ID = os.getenv('MOTION_WORKSPACE_ID')

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

# Function to update a task in Trello
def update_trello_task(trello_card_id, motion_task):
    url = f"https://api.trello.com/1/cards/{trello_card_id}"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'name': motion_task['name'],
        'desc': motion_task.get('description', ''),
        'due': motion_task.get('dueDate'),
        'dueComplete': 'true' if motion_task['status']['name'] == 'Completed' else 'false'
    }
    response = requests.put(url, params=query)
    response.raise_for_status()
    logging.info(f"Trello task {trello_card_id} updated successfully")

# Function to sync completed Motion tasks to Trello
def sync_completed_motion_tasks_to_trello():
    logging.info("Checking for completed tasks in Motion...")
    motion_tasks = get_motion_tasks()
    trello_tasks = get_trello_tasks()

    # Create a dictionary of Trello tasks by name for easy lookup
    trello_task_dict = {task['name']: task for task in trello_tasks}

    for task in motion_tasks:
        if task['status']['name'] == 'Completed' and task['name'] in trello_task_dict:
            trello_task = trello_task_dict[task['name']]
            logging.info(f"Updating Trello task '{trello_task['name']}' with Motion task '{task['name']}' status")
            update_trello_task(trello_task['id'], task)

if __name__ == "__main__":
    # Sync completed tasks from Motion to Trello
    sync_completed_motion_tasks_to_trello()
