import os
import logging
from flask import Flask, request, jsonify
import sync_trello_motion  # Import the sync script

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/webhook', methods=['POST', 'HEAD'])
def handle_webhook():
    if request.method == 'HEAD':
        app.logger.info("Received HEAD request")
        return '', 200
    
    data = request.json
    app.logger.info(f"Received POST request with data: {data}")
    
    try:
        if data['action']['type'] == 'updateCard':
            if 'dueComplete' in data['action']['data']['card'] and data['action']['data']['card']['dueComplete'] == True:
                trello_card_id = data['action']['data']['card']['id']
                # Invoke the sync function
                sync_trello_motion.update_motion_task_with_trello_completion(trello_card_id)
    except KeyError as e:
        app.logger.error(f"Error processing webhook data: {e}")

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
