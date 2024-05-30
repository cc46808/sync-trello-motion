import os
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/webhook', methods=['POST', 'HEAD'])
def handle_webhook():
    if request.method == 'HEAD':
        app.logger.info("Received HEAD request")
        return '', 200
    app.logger.info(f"Received POST request with data: {request.json}")
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
