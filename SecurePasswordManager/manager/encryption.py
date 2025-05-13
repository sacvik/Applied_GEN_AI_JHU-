import base64
import json

def encrypt_data(data):
    json_str = json.dumps(data)
    return base64.b64encode(json_str.encode()).decode()

def decrypt_data(encoded_str):
    decoded_bytes = base64.b64decode(encoded_str.encode())
    return json.loads(decoded_bytes.decode())