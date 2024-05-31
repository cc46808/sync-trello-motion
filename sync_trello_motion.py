import os
import requests
import json
import http.client
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Trello API credentials from environment variables
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
TRELLO_LIST_NAME = os.getenv('TRELLO_LIST_NAME')

# Log the environment variables to debug
logging.debug(f"TRELLO_API_KEY: {TRELLO_API_KEY}")
logging.debug(f"TRELLO_API_TOKEN: {TRELLO_API_TOKEN}")
logging.debug(f"TRELLO_BOARD_ID: {TRELLO_BOARD_ID}")
logging.debug(f"TRELLO_LIST_NAME: {TRELLO_LIST_NAME}")

# Motion API credentials from environment variables
MOTION_API_KEY = os.getenv('MOTION_API_KEY')
MOTION_API_HOST = 'api.usemotion.com'
MOTION_WORKSPACE_ID = os.getenv('MOTION_WORKSPACE_ID')

# Function to get Trello list ID
def get_trello_list_id(board_id, list_name):
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN
    }
    response = requests.get(url, params=query)
    response.raise_for_status()
    lists = response.json()
    for lst in lists:
        if lst['name'] == list_name:
            return lst['id']
    raise ValueError(f"List '{list_name}' not found on board '{board_id}'")

# Function to get Trello tasks
def get_trello_tasks():
    url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/cards"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN
    }
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

# Function to create a task in Motion
def create_motion_task(task):
    conn = http.client.HTTPSConnection(MOTION_API_HOST)
    headers = {
        'Accept': "application/json",
        'Content-Type': 'application/json',
        'X-API-Key': MOTION_API_KEY
    }
    data = {
        'name': task['name'],
        'description': task['desc'],
        'dueDate': task.get('due'),
        'workspaceId': MOTION_WORKSPACE_ID
    }
    json_data = json.dumps(data)
    conn.request("POST", "/v1/tasks", body=json_data, headers=headers)
    res = conn.getresponse()
    response_data = res.read()
    task_response = json.loads(response_data.decode("utf-8"))
    conn.close()
    return task_response

# Function to update a task in Motion
def update_motion_task(task_id, task):
    conn = http.client.HTTPSConnection(MOTION_API_HOST)
    headers = {
        'Accept': "application/json",
        'Content-Type': 'application/json',
        'X-API-Key': MOTION_API_KEY
    }
    data = {
        'name': task['name'],
        'description': task['desc'],
        'dueDate': task.get('due'),
        'status': 'Completed' if task.get('dueComplete') else 'Todo'
    }
    json_data = json.dumps(data)
    conn.request("PATCH", f"/v1/tasks/{task_id}", body=json_data, headers=headers)
    res = conn.getresponse()
    response_data = res.read()
    task_response = json.loads(response_data.decode("utf-8"))
    conn.close()
    return task_response

# Function to create a task in Trello
def create_trello_task(motion_task, trello_list_id):
    url = "https://api.trello.com/1/cards"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'idList': trello_list_id,
        'name': motion_task['name'],
        'desc': motion_task['description'] or '',
        'due': motion_task.get('dueDate')
    }
    response = requests.post(url, params=query)
    response.raise_for_status()
    return response.json()

# Function to update a task in Trello
def update_trello_task(trello_task_id, motion_task):
    url = f"https://api.trello.com/1/cards/{trello_task_id}"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'name': motion_task['name'],
        'desc': motion_task['description'] or '',
        'due': motion_task.get('dueDate'),
        'dueComplete': 'true' if motion_task['status']['name'] == 'Completed' else 'false'
    }
    response = requests.put(url, params=query)
    response.raise_for_status()
    return response.json()

# Function to sync tasks from Trello to Motion
def sync_trello_to_motion():
    logging.debug("Syncing Trello to Motion")
    trello_tasks = get_trello_tasks()
    motion_tasks = get_motion_tasks()

    # Create a dictionary of Motion tasks by name for easy lookup
    motion_task_dict = {task['name']: task for task in motion_tasks}

    for task in trello_tasks:
        if task['name'] in motion_task_dict:
            # Update Motion task if it exists and has changed
            motion_task = motion_task_dict[task['name']]
            motion_status = 'Completed' if task['dueComplete'] else 'Todo'
            if (motion_task['description'] != task['desc'] or 
                motion_task['dueDate'] != task.get('due') or
                motion_task['status']['name'] != motion_status):
                task['status'] = {'name': motion_status}
                update_motion_task(motion_task['id'], task)
                logging.debug(f"Updated Motion task {motion_task['id']} with Trello task {task['id']}")
        else:
            # Create new Motion task if it doesn't exist
            created_task = create_motion_task(task)
            logging.debug(f"Created new Motion task {created_task['id']} from Trello task {task['id']}")

# Function to sync tasks from Motion to Trello
def sync_motion_to_trello():
    logging.debug("Syncing Motion to Trello")
    motion_tasks = get_motion_tasks()
    trello_tasks = get_trello_tasks()
    
    # Create a dictionary of Trello tasks by name for easy lookup
    trello_task_dict = {task['name']: task for task in trello_tasks}
    trello_list_id = get_trello_list_id(TRELLO_BOARD_ID, TRELLO_LIST_NAME)
    
    for task in motion_tasks:
        if task['name'] in trello_task_dict:
            # Update Trello task if it exists and has changed
            trello_task = trello_task_dict[task['name']]
            trello_due_complete = trello_task['dueComplete'] or (task['status']['name'] == 'Completed')
            if (trello_task['desc'] != task['description'] or 
                trello_task['due'] != task.get('dueDate') or
                trello_task['dueComplete'] != trello_due_complete):
                task['dueComplete'] = trello_due_complete
                update_trello_task(trello_task['id'], task)
                logging.debug(f"Updated Trello task {trello_task['id']} with Motion task {task['id']}")
        else:
            # Create new Trello task if it doesn't exist
            created_task = create_trello_task(task, trello_list_id)
            logging.debug(f"Created new Trello task {created_task['id']} from Motion task {task['id']}")

# Function to perform two-way sync
def two_way_sync():
    try:
        sync_trello_to_motion()
        sync_motion_to_trello()
    except Exception as e:
        logging.error(f"Error during sync: {e}")

# Function to update Motion task when Trello task is completed
def update_motion_task_with_trello_completion(trello_card_id):
    logging.debug(f"Updating Motion task with completion status from Trello card {trello_card_id}")
    trello_tasks = get_trello_tasks()
    for task in trello_tasks:
        if task['id'] == trello_card_id:
            # Find the corresponding Motion task by name or another identifier
            motion_tasks = get_motion_tasks()
            for motion_task in motion_tasks:
                if motion_task['name'] == task['name']:
                    # Update the Motion task status to Completed
                    update_motion_task(motion_task['id'], task)
                    logging.debug(f"Updated Motion task {motion_task['id']} for Trello card {trello_card_id}")
                    return
            logging.debug(f"No corresponding Motion task found for Trello card {trello_card_id}")
            return
    logging.debug(f"No Trello card found with ID {trello_card_id}")

# Perform the sync immediately (only if this script is run directly)
if __name__ == "__main__":
    two_way_sync()
