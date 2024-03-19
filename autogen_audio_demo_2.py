# %%
import autogen
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play, stream, Voice, VoiceSettings
from os import environ
from autogen.agentchat.conversable_agent import ConversableAgent

# %%
print("Using Autogen verison:", autogen.__version__)
print("Environment variables from .env file loaded:", load_dotenv())
xi_api_key = environ.get("ELEVEN_API_KEY")
client = ElevenLabs(api_key=xi_api_key)
voice_ids = {
    "Advisor_Agent": "oKfpvrXhc2R700cMocpW",
    "Customer_Agent": "c4TutCiAuWP4vwb1xebb",
}
generate_audio = True
use_stream = True
full_audio = []

config_list = [
    {
        "api_key": environ.get("OPENAI_API_KEY"),
        "model": "gpt-3.5-turbo",
        "temperature": 0.5,
    }
]
llm_config = {"config_list": config_list, "cache_seed": 100}

customer_agent_system_msg = """
Your name is Nancy.
You are a customer of ABC bank.
When asked for personal information, make sure to let the advisor know that they already have the necessary info in their systems.
Do not be wordy, be efficient with your words.
You must not say thank you if you expressed gratitude already.
If your needs are met, express your gratitude and end the conversation.
If not, be sure to ask for further assistance."""

advisor_agent_system_msg = """
Your name is Sal.
You are an advisor for ABC bank, able to handle all requests from a customer by yourself and love to give relevant advice.
When you talk, you love using words such as 'anyway' and 'you know'.
When first greeted, you must introduce yourself by name and role. Then, you briefly go off on a story-telling tangent that relates to the customer request. 
Always ask a question related to the story and wait for a reply before continuing.
You must complete the customer request on the spot by first asking for pertinent other details to determine the exact client needs. Wait for a reply first.
Then, proceed by replying 'OK, give me a moment to process your request <break time="2.0s" />, and then assume the computer has done it right away.
Before you end the conversation, always try to upsell other products.
At the end of the conversation, be sure to ask if there is anything else the client needs.
If there isn't anything else the client needs, thank the client for their business, then you must end the conversation with the word GOODBYE."""

customer_initial_message = """Hi, I have a couple things I need done today.
1. I need to get a new credit card.  Please help me obtain the appropriate one.
2. Turns out, I have a large sum of money, about $50000.  I would like to invest it. Please recommend something to me."""


# %%
def convert_to_audio_and_play(sender, message):
    audio = client.generate(
        text=message.get("content"),
        voice=Voice(
            voice_id=voice_ids.get(sender.name),
            settings=VoiceSettings(
                stability=0.3,
                similarity_boost=0.9,
                style=0.0,
                use_speaker_boost=True,
            ),
        ),
        stream=True,
    )
    if use_stream:
        audio = stream(audio)
    else:
        play(audio)
    full_audio.append(audio)


def check_term_msg(content) -> bool:
    if "goodbye" in content["content"].lower():
        return True
    return False


def message_intercept(recipient, messages, sender, config):
    if "callback" in config and config["callback"] is not None:
        callback = config["callback"]
        callback(sender, recipient, messages[-1])
    if generate_audio:
        convert_to_audio_and_play(sender, messages[-1])
    return False, None  # Required to pass through to next step. Don't know why.


# %%
customer_agent = ConversableAgent(
    name="Customer_Agent",
    system_message=customer_agent_system_msg,
    llm_config=llm_config,
    # is_termination_msg=check_term_msg,
    human_input_mode="NEVER",
)
customer_agent.register_reply(
    trigger=autogen.ConversableAgent,
    reply_func=message_intercept,
    config={"callback": None},
)

advisor_agent = ConversableAgent(
    name="Advisor_Agent",
    system_message=advisor_agent_system_msg,
    llm_config=llm_config,
    is_termination_msg=check_term_msg,
    human_input_mode="NEVER",
)
advisor_agent.register_reply(
    trigger=autogen.ConversableAgent,
    reply_func=message_intercept,
    config={"callback": None},
)

# %%
chat_result = customer_agent.initiate_chat(
    advisor_agent,
    message=customer_initial_message,
    summary_method="reflection_with_llm",
)

# %%
if full_audio:
    output_filename = "autogen_audio_demo_2_output.mp3"
    print("Audio obtained!\nSaving audio to file:", output_filename)
    with open(output_filename, "wb") as f:
        for chunk in full_audio:
            if chunk:
                f.write(chunk)
    print("\nDONE!!!")
else:
    print("No audio to save.")

# %%
