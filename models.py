import requests
from pprint import pprint

xi_api_key = open(".env","r").readline().split("=")[1].strip()

url = "https://api.elevenlabs.io/v1/models"

headers = {
  "xi-api-key": xi_api_key
}

response = requests.get(url, headers=headers)
pprint(response.json())
