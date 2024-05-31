import os
from flask import Flask, request, jsonify
import logging
import sync_trello_motion

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    logging.info(f"Received POST request with data: {data}")
    
    if 'action' in data and 'card' in data['action']['data']:
        card_id = data['action']['data']['card']['id']
        logging.info(f"Card ID to update in Motion: {card_id}")
        try:
            sync_trello_motion.update_motion_task_with_trello_status(card_id)
        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return jsonify({'error': str(e)}), 500

    return '', 200

if __name__ == "__main__":
    app.run(debug=True, port=os.getenv('PORT', 5000))
