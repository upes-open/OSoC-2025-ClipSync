# 📋 ClipSync Lite

**ClipSync Lite** is a minimal Python-based clipboard sync tool that enables **bidirectional text sharing** between a Windows PC and an Android device over a local network. It uses AES encryption for privacy and a simple client-server model using Flask and requests.

### 🚀 Features
- Bidirectional clipboard sync (Win ↔ Android)
- AES-256 encryption
- Flask-based REST endpoints
- Text-only sync over local Wi-Fi

### 📦 Requirements
- Python 3.9+
- pyperclip
- pycryptodome
- Flask
- requests
- (Kivy or Chaquopy for Android)

### 🛠️ How it Works
Each device:
- Watches its clipboard
- Sends encrypted content to the other device's Flask server
- Receives and decrypts clipboard updates

> Configuration is done via a shared `config.json` file.

---
