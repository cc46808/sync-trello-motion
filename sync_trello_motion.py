import os
import requests
import json
import http.client
import logging

# Set up logging
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

# Function to update Motion task when Trello task status changes
def update_motion_task_with_trello_status(trello_card_id):
    logging.debug(f"Updating Motion task with status from Trello card {trello_card_id}")
    trello_tasks = get_trello_tasks()
    for task in trello_tasks:
        if task['id'] == trello_card_id:
            # Find the corresponding Motion task by name or another identifier
            motion_tasks = get_motion_tasks()
            for motion_task in motion_tasks:
                if motion_task['name'] == task['name']:
                    # Update the Motion task status
                    update_motion_task(motion_task['id'], task)
                    logging.debug(f"Updated Motion task {motion_task['id']} for Trello card {trello_card_id}")
                    return
            logging.debug(f"No corresponding Motion task found for Trello card {trello_card_id}")
            return
    logging.debug(f"No Trello card found with ID {trello_card_id}")

# Perform the sync immediately (only if this script is run directly)
if __name__ == "__main__":
    logging.debug("This script is intended to be imported and used as a module.")
