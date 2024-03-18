# %%
from elevenlabs.client import ElevenLabs
from elevenlabs import play, stream, save, Voice, VoiceSettings
from pprint import pprint
from dotenv import load_dotenv
from os import environ

print("Environment variables from .env file loaded:", load_dotenv())
xi_api_key = environ.get("ELEVEN_API_KEY")
client = ElevenLabs(api_key=xi_api_key)

# %%
# voice_id = "c4TutCiAuWP4vwb1xebb" # Annie-Beth Southern Accent
voice_id = "XjffbH7iSzh991n23AaG"  # Kelly Teenager

# %%
voice_list = client.voices.get_all()
pprint(voice_list)

# %%
models = client.models.get_all()
pprint(models)

# %%
audio = client.generate(
    # api_key="YOUR_API_KEY", (Defaults to os.getenv(ELEVEN_API_KEY))
    text="Hi",
    voice="Rachel",
    #   model="eleven_multilingual_v2",
    model="eleven_monolingual_v1",
)

play(audio)

# %%
audio = client.generate(
    text="Hello",
    voice=Voice(
        voice_id="EXAVITQu4vr4xnSDxMaL",
        settings=VoiceSettings(
            stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True
        ),
    ),
)

play(audio)

# %%
voice = client.clone(
    api_key=xi_api_key,  # (Defaults to os.getenv(ELEVEN_API_KEY))
    name="testing_from_lib",
    description="A male. Unkown origin.",  # Optional
    # files=["./sample_0.mp3", "./sample_1.mp3", "./sample_2.mp3"],
    files=["./samples/taunt.wav"],
)

audio = client.generate(text="Hi", voice=voice)
print("Save this:", voice.voice_id)

play(audio)

save(audio, "test_audio_save.mp3")


# %%
def text_stream():
    yield "Hi "
    yield "this is me!"


audio_stream = client.generate(
    api_key=xi_api_key,  # (Defaults to os.getenv(ELEVEN_API_KEY))
    text=text_stream(),
    voice="Nicole",
    model="eleven_monolingual_v1",
    stream=True,
)

stream(audio_stream)

# %%
# NOT WORKING YET!
# model_id = "eleven_multilingual_sts_v2"
model_id = "eleven_english_sts_v2"

audio = client.speech_to_speech.convert(
    audio="./samples/taunt.wav", voice_id=voice_id, model_id=model_id
)
# client.speech_to_speech.convert_as_stream(
#     voice_id="string",
#     optimize_streaming_latency=1,
# )

# %%
