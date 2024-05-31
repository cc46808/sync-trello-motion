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
    app.logger.info(f"Received POST request with data: {request.json}")
    
    data = request.json
    if 'action' in data and 'data' in data['action']:
        card_id = data['action']['data']['card']['id']
        app.logger.info(f"Card ID to update in Motion: {card_id}")
        sync_trello_motion.update_motion_task_with_trello_status(card_id)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
