import os
import requests
import json
import http.client
from datetime import datetime

# Trello API credentials from environment variables
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_API_TOKEN = os.getenv('TRELLO_API_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
TRELLO_LIST_NAME = os.getenv('TRELLO_LIST_NAME')  # Add the list name to your environment variables

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
    print("Motion API Response Status:", res.status)
    print("Motion API Response Data:", data)
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
    print("Create Motion Task Response Status:", res.status)
    print("Create Motion Task Response Data:", response_data)
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
        'status': 'Completed' if task.get('dueComplete') else 'Todo'  # Adjust according to Motion API status values
    }
    json_data = json.dumps(data)
    conn.request("PATCH", f"/v1/tasks/{task_id}", body=json_data, headers=headers)
    res = conn.getresponse()
    response_data = res.read()
    print("Update Motion Task Response Status:", res.status)
    print("Update Motion Task Response Data:", response_data)
    task_response = json.loads(response_data.decode("utf-8"))
    conn.close()
    return task_response

# Function to format date for Trello
def format_date_for_trello(date_str):
    if date_str:
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.isoformat()
        except ValueError:
            return date_str
    return None

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
    print("Created Trello Task Response Status:", response.status_code)
    print("Created Trello Task Response Data:", response.json())

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
    print("Updated Trello Task Response Status:", response.status_code)
    print("Updated Trello Task Response Data:", response.json())

# Function to sync tasks from Trello to Motion
def sync_trello_to_motion():
    trello_tasks = get_trello_tasks()
    motion_tasks = get_motion_tasks()

    print("Trello Tasks:", trello_tasks)
    print("Motion Tasks:", motion_tasks)

    # Create a dictionary of Motion tasks by name for easy lookup
    motion_task_dict = {task['name']: task for task in motion_tasks}

    for task in trello_tasks:
        if task['name'] in motion_task_dict:
            # Update Motion task if it exists and has changed
            motion_task = motion_task_dict[task['name']]
            if (motion_task['description'] != task['desc'] or 
                motion_task['dueDate'] != task.get('due') or
                motion_task['status']['name'] != ('Completed' if task['dueComplete'] else 'Todo')):
                update_motion_task(motion_task['id'], task)
        else:
            # Create new Motion task if it doesn't exist
            create_motion_task(task)

# Function to sync tasks from Motion to Trello
def sync_motion_to_trello():
    motion_tasks = get_motion_tasks()
    trello_tasks = get_trello_tasks()

    print("Motion Tasks:", motion_tasks)
    print("Trello Tasks:", trello_tasks)

    # Create a dictionary of Trello tasks by name for easy lookup
    trello_task_dict = {task['name']: task for task in trello_tasks}
    trello_list_id = get_trello_list_id(TRELLO_BOARD_ID, TRELLO_LIST_NAME)

    for task in motion_tasks:
        if task['name'] in trello_task_dict:
            # Update Trello task if it exists and has changed
            trello_task = trello_task_dict[task['name']]
            if (trello_task['desc'] != task['description'] or 
                trello_task['due'] != task.get('dueDate') or
                (task['status']['name'] == 'Completed' and not trello_task['dueComplete'])):
                update_trello_task(trello_task['id'], task)
        else:
            # Create new Trello task if it doesn't exist
            create_trello_task(task, trello_list_id)

# Function to perform two-way sync
def two_way_sync():
    try:
        sync_trello_to_motion()
        sync_motion_to_trello()
    except Exception as e:
        print(f"Error during sync: {e}")

# Perform the sync immediately
two_way_sync()
