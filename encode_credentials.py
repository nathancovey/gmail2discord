import base64

with open('credentials.json', 'rb') as f:
    encoded = base64.b64encode(f.read())
    with open('credentials_base64.txt', 'wb') as f_encoded:
        f_encoded.write(encoded)
