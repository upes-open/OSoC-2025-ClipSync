from flask import Flask, request, jsonify
import pyperclip

app = Flask(__name__)

@app.route('/clipboard', methods=['POST'])
def receive_clipboard():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'status': 'error', 'message': 'No text provided'}), 400

    received_text = data['text']
    pyperclip.copy(received_text)  # Update clipboard
    print(f"Clipboard updated with: {received_text}")

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
