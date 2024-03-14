# %%
# Imports and init
from elevenlabs.client import ElevenLabs
from elevenlabs import generate, play, voices, clone, stream, Voice, VoiceSettings
from pprint import pprint
from dotenv import load_dotenv
from os import environ

print("Environment variables from .env file loaded:", load_dotenv())
xi_api_key = environ.get("ELEVEN_API_KEY")
client = ElevenLabs(api_key=xi_api_key)

# %%
# Define the voices
voice_ids = {"A": "tKZQTIqwDrPzLv6MrPxF", "C": "EGkVDGCzQJg7JwE4bS1l"}
model = "eleven_turbo_v2"

# %%
# Script with emotional hints
script = """
A: "Hello, Mr. Smith, my name is Sana, how may I help you?"
C: "You'd better be able to help me! -- You crooks stole all my money!"
A: "I'm sorry to hear that sir... Can you tell me what happened?"
C: "Check my account! -- There's no money in it! -- I had 6 dollars in my account just yesterday! -- Now it's gone!"
A: "Oh no..."
C: "I'm stuck in the middle of nowhere right now! Give me my money back so I can get home!"
A: "Give me one second to find the problem." <break time="2.0s" /> "It seems you were charged the monthly account fee. However...I can refund it for you this one time."
C: "JUST HURRY UP AND DO IT!"
A: "Just one more second." <break time="1.0s" /> "Done! The 6 dollars is back in your account Mr. Smith"
C: "FINALLY!"
A: "Thank you for choosing RBC. Have a nice day!"
""".strip()

conversation = script.split("\n")

# %%
for line in conversation:
    if line.startswith("A:"):
        print("Using advisor voice")
    elif line.startswith("C:"):
        print("Using customer voice")
    else:
        print("Don't know which voice should I use...")
        continue
    audio = generate(
        text=line[3:],
        voice=Voice(
            voice_id=voice_ids.get(line[0]),
            settings=VoiceSettings(
                stability=0.2,
                similarity_boost=0.5,
                style=0.0,
                use_speaker_boost=True,
            ),
        ),
    )
    play(audio)

# %%
