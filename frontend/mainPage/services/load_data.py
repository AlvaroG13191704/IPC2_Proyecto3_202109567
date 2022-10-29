import requests
import json

def get_data():
    response = requests.get('http://localhost:5000/consultarDatos')
    data = json.loads(response.text)
    return data