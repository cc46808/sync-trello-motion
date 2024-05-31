import os
from flask import Flask, request # type: ignore
import logging
import sync_trello_motion as sync_trello_motion 

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.json
    logging.info(f"Received POST request with data: {data}")

    try:
        card_id = data['action']['data']['card']['id']
        logging.info(f"Card ID to update in Motion: {card_id}")
        sync_trello_motion.update_motion_task_with_trello_status(card_id)
        return '', 200
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return str(e), 500

if __name__ == "__main__":
    app.run(debug=True)
