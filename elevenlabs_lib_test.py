# %%
from elevenlabs.client import ElevenLabs
from elevenlabs import generate, play, voices, clone, stream, Voice, VoiceSettings
from pprint import pprint

# %%
xi_api_key = open(".env", "r").readline().split("=")[1].strip()
# voice_id = "c4TutCiAuWP4vwb1xebb" # Annie-Beth Southern Accent
voice_id = "XjffbH7iSzh991n23AaG"  # Kelly Teenager

client = ElevenLabs(api_key=xi_api_key)

# %%
voice_list = voices()
pprint(voice_list)

# %%
models = client.models.get_all()
pprint(models)

# %%
audio = generate(
    # api_key="YOUR_API_KEY", (Defaults to os.getenv(ELEVEN_API_KEY))
    text="Hi",
    voice="Rachel",
    #   model="eleven_multilingual_v2",
    model="eleven_monolingual_v1",
)

# %%
play(audio)

# %%
audio = generate(
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
voice = clone(
    api_key=xi_api_key,  # (Defaults to os.getenv(ELEVEN_API_KEY))
    name="Myself",
    description="A male with a Chinese/Canadian accent.",  # Optional
    # files=["./sample_0.mp3", "./sample_1.mp3", "./sample_2.mp3"],
    files=["./samples/taunt.wav"],
)

audio = generate(text="Hi", voice=voice)
print("Save this:", voice.voice_id)

# %%
play(audio)


# %%
def text_stream():
    yield "Hi "
    yield "this is me!"


audio_stream = generate(
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
