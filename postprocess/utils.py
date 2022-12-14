import requests
import json

def launch(promt):
    r = requests.post("http://localhost:8080", promt)
    response = json.loads(r.text)
    if not response["success"]:
        raise Exception("Error: " + response["message"])
    return response["prefix"]
    
