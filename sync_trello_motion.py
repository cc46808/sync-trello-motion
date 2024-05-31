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
    logging.debug(f"Creating new Motion task with data: {data}")
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
    logging.debug(f"Updating Motion task {task_id} with data: {data}")
    conn.request("PATCH", f"/v1/tasks/{task_id}", body=json_data, headers=headers)
    res = conn.getresponse()
    response_data = res.read()
    task_response = json.loads(response_data.decode("utf-8"))
    conn.close()
    return task_response

# Function to update Motion task with Trello status
def update_motion_task_with_trello_status(trello_card_id):
    trello_tasks = get_trello_tasks()
    motion_tasks = get_motion_tasks()
    
    logging.debug(f"Trello tasks: {trello_tasks}")
    logging.debug(f"Motion tasks: {motion_tasks}")
    
    for task in trello_tasks:
        if task['id'] == trello_card_id:
            for motion_task in motion_tasks:
                if motion_task['name'] == task['name']:
                    update_motion_task(motion_task['id'], task)
                    logging.info(f"Updated Motion task {motion_task['id']} for Trello card {trello_card_id}")
                    return
            logging.info(f"No corresponding Motion task found for Trello card {trello_card_id}. Creating new Motion task.")
            create_motion_task(task)
            return
    logging.info(f"No Trello card found with ID {trello_card_id}")

# Flask app to handle webhooks from Trello
# from flask import Flask, request, jsonify

# app = Flask(__name__)

# @app.route('/webhook', methods=['POST'])
# def handle_webhook():
#     data = request.json
#     logging.info(f"Received POST request with data: {data}")

#     if 'action' in data:
#         action = data['action']
#         if 'data' in action and 'card' in action['data']:
#             card_id = action['data']['card']['id']
#             logging.info(f"Card ID to update in Motion: {card_id}")
#             try:
#                 update_motion_task_with_trello_status(card_id)
#             except Exception as e:
#                 logging.error(f"Exception occurred: {e}")
#                 return jsonify({'status': 'error', 'message': str(e)}), 500
#     return jsonify({'status': 'success'}), 200

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
