# %%
import requests

xi_api_key = open(".env", "r").readline().split("=")[1].strip()

CHUNK_SIZE = 1024

# voice_id = "c4TutCiAuWP4vwb1xebb" # Annie-Beth Southern Accent
# voice_id = "XjffbH7iSzh991n23AaG" # Kelly Teenager
voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel, the first on the list (premade)
# model_id = "eleven_multilingual_sts_v2"
model_id = "eleven_english_sts_v2"

url = f"https://api.elevenlabs.io/v1/speech-to-speech/{voice_id}"

headers = {
    # "Content-Type": "multipart/form-data",
    "xi-api-key": xi_api_key
}
audio_file = "./samples/15-seconds-of-silence.mp3"
audio_file = "./samples/taunt.wav"

# %%
print("Reference audio file to dub:", audio_file)
with open(audio_file, "rb") as f:
    payload = {
        "audio": f.read(),
        # "model_id": str(model_id),
        # "voice_settings":{
        #     "stability": 0.1,
        #     "similarity_boost": 1
        # }
    }
    # payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"audio\"\r\n\r\n{f.read()}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"model_id\"\r\n\r\n{model_id}\r\n-----011000010111000001101001--\r\n\r\n"

print("\nGetting the audio response from ElevenLabs...")
response = requests.post(
    url, files=payload, data={"model_id": model_id}, headers=headers
)

# %%
if response:
    output_filename = "sts-output.mp3"
    print("Audio obtained!\nSaving audio to file:", output_filename)
    with open(output_filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
    print("\nDONE!!!")
else:
    print("Unable to get audio.", response)
# %%
