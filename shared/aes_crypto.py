import base64
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

BLOCK_SIZE = 16  # AES block size (in bytes)

def encrypt(plaintext: str, key: bytes) -> str:
    iv = os.urandom(BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = pad(plaintext.encode(), BLOCK_SIZE)
    encrypted = cipher.encrypt(padded)
    return base64.b64encode(iv + encrypted).decode()

def decrypt(encoded_data: str, key: bytes) -> str:
    raw = base64.b64decode(encoded_data)
    iv = raw[:BLOCK_SIZE]
    encrypted = raw[BLOCK_SIZE:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted)
    unpadded = unpad(decrypted, BLOCK_SIZE)
    return unpadded.decode()
