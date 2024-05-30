import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/webhook', methods=['POST', 'HEAD'])
def handle_webhook():
    if request.method == 'HEAD':
        # Trello sends a HEAD request to verify the endpoint
        return ('', 200)
    # Process POST requests with actual data
    data = request.json
    print("Received webhook:", data)  # Log the webhook data
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
