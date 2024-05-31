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
    
    # Extract the relevant information from the webhook payload
    action = request.json.get('action')
    if action and action.get('type') == 'updateCard':
        card = action.get('data', {}).get('card', {})
        trello_card_id = card.get('id')
        if card.get('dueComplete'):
            # Update the corresponding task in Motion as completed
            sync_trello_motion.update_motion_task_with_trello_completion(trello_card_id)
    
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
