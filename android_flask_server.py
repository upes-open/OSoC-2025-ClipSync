import os
import json
import base64
from flask import Flask, request, jsonify
from Crypto.Cipher import AES
import subprocess

# Load config from shared/config.json
with open('shared/config.json', 'r') as f:
    config = json.load(f)

AES_KEY = base64.b64decode(config['aes_key'])
AES_IV = base64.b64decode(config['iv'])
LOCAL_PORT = config['local_port']

app = Flask(__name__)

@app.route('/clipboard', methods=['POST'])
def clipboard():
    data = request.get_json()
    if not data or 'data' not in data:
        return jsonify({"error": "Missing 'data' field"}), 400
    try:
        encrypted = base64.b64decode(data['data'])
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        decrypted = cipher.decrypt(encrypted)
        pad_len = decrypted[-1]
        clipboard_text = decrypted[:-pad_len].decode('utf-8')
        # Set clipboard using Termux:API
        subprocess.run(['termux-clipboard-set', clipboard_text])
        print(f"Clipboard updated: {clipboard_text}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=LOCAL_PORT)
