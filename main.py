import requests

xi_api_key = open(".env","r").readline().split("=")[1].strip()

CHUNK_SIZE = 1024

# voice_id = "c4TutCiAuWP4vwb1xebb" # Annie-Beth Southern Accent
voice_id = "XjffbH7iSzh991n23AaG" # Kelly Teenager
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

querystring = {
  "output_format":"mp3_22050_32",
  "optimize_streaming_latency":"0"
} # output_format default: mp3_44100_128, optimize_streaming_latency default: 0

headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": xi_api_key
}

text = input("Text to convert to audio:")
if not text:
  text = """
Here are some phrases to showcase my ability: 
  Momma and Daddy said so!
  He's such a sweet fellow. 
  Give me that yellow mustard for my dog. 
  My truck has a flat tire. 
  Have we met before? 
  Say grace before you eat. 
  Get your boots off the table!
  I can't fit in this wedding dress, Momma! 
  I'm going to get you, Bubba! 
  Y'all come back now! 
  You best go back to school.
  I like your pickup truck.
  Come on, girl!
  Eat your green peas, sweetie.
  He looks like a red neck."""
  print("\nNo text provided. Using this text:\n", text)

data = {
  "text": text,
  "model_id": "eleven_monolingual_v1",
#  "model_id": "eleven_turbo_v2",
  "voice_settings": {
    "stability": 0.1,
    "similarity_boost": 1
  }
}

print("\nGetting the audio response from ElevenLabs...")
response = requests.post(url, json=data, headers=headers, params=querystring)

if response:
  output_filename = "output.mp3"
  print("Audio obtained!\nSaving audio to file:", output_filename)
  with open(output_filename, 'wb') as f:
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
      if chunk:
        f.write(chunk)
  print("\nDONE!!!")
else:
  print("Unable to get audio.", response)
