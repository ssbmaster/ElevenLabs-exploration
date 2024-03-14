# %%
# Get list of all voices and attributes
import requests
import json
from dotenv import load_dotenv
from os import environ

print("Environment variables from .env file loaded:", load_dotenv())
xi_api_key = environ.get("ELEVEN_API_KEY")

url = "https://api.elevenlabs.io/v1/voices"

headers = {"xi-api-key": xi_api_key}

response = requests.get(url, headers=headers)
voices = json.loads(response.text)["voices"]
print(json.dumps(voices, indent=4))

# %%
# Get global default voice settings
url = "https://api.elevenlabs.io/v1/voices/settings/default"
response = requests.get(url, headers=headers)
print(json.dumps(json.loads(response.text), indent=4))

# %%
# Get a specific voice's attributes
# NOTE: requests.delete() will delete the specified voice
voice_id = voices[0]["voice_id"]
url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
response = requests.get(url, headers=headers)
print(json.dumps(json.loads(response.text), indent=4))

# %%
# Get a specific voice's default voice settings
# NOTE: requests.post() with appropriate json will edit/update the settings
voice_id = voices[0]["voice_id"]
url = f"https://api.elevenlabs.io/v1/voices/{voice_id}/settings"
response = requests.get(url, headers=headers)
print(json.dumps(json.loads(response.text), indent=4))

# %%
# Add a voice
# NOTE: Can add description and labels (serialize by: str(json.dumps({}))) to data in addition to name
# NOTE: Make sure to record the voice_id that gets returned
url = "https://api.elevenlabs.io/v1/voices/add"
audio_file = "./samples/taunt.wav"
name = "my_custom_voice_1"

print("Audio file to add:", audio_file)
with open(audio_file, "rb") as f:
    payload = {
        "files": f.read(),
    }
response = requests.post(url, files=payload, data={"name": name}, headers=headers)
print(json.dumps(json.loads(response.text), indent=4))

# %%
# Edit a specific voice, add description
url = f"https://api.elevenlabs.io/v1/voices/{voice_id}/edit"
audio_file = "./samples/taunt.wav"
name = "my_custom_voice_1"
description = "This is my custom voice #1"
labels = str(json.dumps({"accent": "american", "age": "middle_aged"}))
response = requests.post(
    url,
    data={"name": name, "description": description, "labels": labels},
    headers=headers,
)
print(json.dumps(json.loads(response.text), indent=4))

# %%
