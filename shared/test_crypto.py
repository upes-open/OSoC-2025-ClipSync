from aes_crypto import encrypt, decrypt
import os

key = os.urandom(32)  # AES-256 key
message = "Hello from ClipSync!"

encrypted = encrypt(message, key)
print("Encrypted:", encrypted)

decrypted = decrypt(encrypted, key)
print("Decrypted:", decrypted)

assert decrypted == message, " Decryption failed"
print("AES encryption/decryption test passed!!")
