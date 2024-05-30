import os
import requests
import json
import http.client

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

# Function to create a task in Trello
def create_trello_task(task):
    url = "https://api.trello.com/1/cards"
    query = {
        'key': TRELLO_API_KEY,
        'token': TRELLO_API_TOKEN,
        'idList': TRELLO_BOARD_ID,
        'name': task['name'],
        'desc': task['description'],
        'due': task.get('dueDate')
    }
    response = requests.post(url, params=query)
    response.raise_for_status()
    return response.json()

# Function to sync tasks from Trello to Motion
def sync_trello_to_motion():
    trello_tasks = get_trello_tasks()
    motion_tasks = get_motion_tasks()

    print("Trello Tasks:", trello_tasks)
    print("Motion Tasks:", motion_tasks)

    # Create a set of Motion task names to avoid duplicates
    motion_task_names = {task['name'] for task in motion_tasks}

    for task in trello_tasks:
        if task['name'] not in motion_task_names:
            create_motion_task(task)

# Function to sync tasks from Motion to Trello
def sync_motion_to_trello():
    motion_tasks = get_motion_tasks()
    trello_tasks = get_trello_tasks()

    print("Motion Tasks:", motion_tasks)
    print("Trello Tasks:", trello_tasks)

    # Create a set of Trello task names to avoid duplicates
    trello_task_names = {task['name'] for task in trello_tasks}

    for task in motion_tasks:
        if task['name'] not in trello_task_names:
            create_trello_task(task)

# Function to perform two-way sync
def two_way_sync():
    try:
        sync_trello_to_motion()
        sync_motion_to_trello()
    except Exception as e:
        print(f"Error during sync: {e}")

# Perform the sync immediately
two_way_sync()
