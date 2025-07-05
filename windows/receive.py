from flask import Flask, request, jsonify
import pyperclip
import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'shared', 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

config = load_config()
PORT = config.get('local_port', 5000)


app = Flask(__name__)

@app.route('/clipboard', methods=['POST'])
def receive_clipboard():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'status': 'error', 'message': 'No text provided'}), 400

    received_text = data['text']
    
    try:
        pyperclip.copy(received_text)
        print(f"Clipboard updated with: {received_text}")
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        print(f"Clipboard update failed: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to set clipboard'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
