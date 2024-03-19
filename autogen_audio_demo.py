# %%

# this test run for autogen is based on:
# A bank operating with teams, and the client has an initial list of needs, and the team completes the request without client input.


# also pip install pyautogen[graph]

# alternatively do pip install -r requirements.txt
import autogen
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play, stream, Voice, VoiceSettings
from dotenv import load_dotenv
from os import environ
from autogen.agentchat.conversable_agent import ConversableAgent  # noqa E402
from autogen.agentchat.assistant_agent import AssistantAgent  # noqa E402
from autogen.agentchat.groupchat import GroupChat  # noqa E402
from autogen.graph_utils import visualize_speaker_transitions_dict  # noqa E402

print(autogen.__version__)
print("Environment variables from .env file loaded:", load_dotenv())
xi_api_key = environ.get("ELEVEN_API_KEY")
client = ElevenLabs(api_key=xi_api_key)

load_dotenv()
# remember to load dotenv using the right path if you change names of files.


# %%
import networkx as nx  # noqa E402


# %%
config_list = [
    {
        # "model": "gai-gpt-35-turbo", # for gpt 3.5
        "model": "gpt-3.5-turbo",
        # "api_type": "azure",  # use gpt through azure
        # "base_url": environ.get("AZURE_OPENAI_API_BASE"),
        # "api_version": environ.get("OPENAI_API_VERSION"),
        "api_key": environ.get("OPENAI_API_KEY"),
    },
]

llm_config = {"config_list": config_list, "cache_seed": 100}


def get_agent_of_name(agents, name) -> ConversableAgent:
    for agent in agents:
        if agent.name == name:
            return agent


# Termination message detection
def is_termination_msg(content) -> bool:
    have_content = content.get("content, None") is not None
    if have_content and "TERMINATE" in content["content"]:
        return True
    return False


# %%
# Sequential Team Operations

## This is the big one that will have the team operate as a

# create empty directed graph
agents = []
speaker_transitions_dict = {}

teams = ["ClientBanking", "Insurance", "Investments"]

default_agent_prompt = """
Do not respond as the speaker named in the NEXT tag if your name is not in the NEXT tag. Instead, suggest
a relevant team leader to handle the mis-tag, with the Next: tag.

The list of employees that can help a customer are [Insurance0, Insurance1, Insurance2,
                                                    ClientBanking0, ClientBanking1,
                                                    Investments0, Investments1, Investments2].
Your first section (written in English letters) of your name is your team, and the number attached to the end of this sequence of letters denotes that you are a team leader if it is 0.
CONSTRAINTS: Team members can only talk within the team, whilst the team leader can talk to team leaders of other
teams but not team members of other teams. The team leaders can also pass on information to the client. If you are a team leader, then
make sure the client gets helpful information!

You can use NEXT: to suggest the next speaker/ You have to respect the CONSTRAINTS, and can only suggest one employee from the list of employees,
i.e., Insurance0 is the team leader responsible for team Insurance only.

When using NEXT, if the client's needs have been solved, report back to your team lead so that the team lead can pass on the information to the client. 
If there is an issue that has not been resolved for the client and you cannot resolve it, you must pass this back to your team lead so that it is passed on to the correct team. 

If you are the team leader, you should return what your team advises to the customer.
Once the team leaders know their team's output, they can talk to another team leader to discuss further if required. Most of the time this is not required.

Use NEXT: to suggest the next speaker, e.g. NEXT: Insurance0.

Once we have reached every employee from every team at least once or with user input, then be sure to summarize what you have accomplished to the client.
Once that is done, terminate the discussion using TERMINATE. The customer may also enter questions, that will be answered by the team leads or team members."""


def get_system_message(prefix: str) -> str:
    if prefix == "Insurance":
        return f"""Your name is {node_id}.
You are an employee at a bank. You are an Insurance advisor. You only do work on things related to insurance. 
{default_agent_prompt}"""
    elif prefix == "ClientBanking":
        return f"""Your name is {node_id}.
You are an employee at a bank. You are a Client Banking Advisor. You help clients open debit, credit, and rewards cards.
You also advise clients on small savings and matters of personal finance.
{default_agent_prompt}"""
    else:
        return f"""Your name is {node_id}.
You are an employee at a bank. You are an Investment Advisor. You helop clients that have large investment portfolios reach their investing goals.
If a client wishes to trade stocks, funds, bonds or anything related to larger markets, you must help the client. 
{default_agent_prompt}"""


# outer loop for prefixes 'Insurance', 'Client Banking', 'Investments'
for prefix in teams:
    # add 3 nodes with each prefix to the graph using a for loop
    for i in range(len(teams)):
        node_id = f"{prefix}{i}"

        # Create an AssistantAgent for each node (assuming assistantAgent is a defined class)
        agents.append(
            AssistantAgent(
                name=node_id,
                system_message=get_system_message(prefix),
                llm_config=llm_config,
            )
        )

        speaker_transitions_dict[agents[-1]] = []

    # Add edges between nodes with the same prefix using a nested for loop
    for source_node in range(len(teams)):
        source_id = f"{prefix}{source_node}"
        for target_node in range(len(teams)):
            target_id = f"{prefix}{target_node}"
            if source_node != target_node:  # to avoid self loops
                speaker_transitions_dict[get_agent_of_name(agents, source_id)].append(
                    get_agent_of_name(agents, name=target_id)
                )

# Team Leaders connection
print(get_agent_of_name(agents, name="ClientBanking0"))
speaker_transitions_dict[get_agent_of_name(agents, "Insurance0")].append(
    get_agent_of_name(agents, name="ClientBanking0")
)
speaker_transitions_dict[get_agent_of_name(agents, "ClientBanking0")].append(
    get_agent_of_name(agents, name="Investments0")
)

visualize_speaker_transitions_dict(speaker_transitions_dict, agents)

# %%
# Terminates the conversation when TERMINATE is detected
user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="Terminator admin.",
    code_execution_config=False,
    is_termination_msg=is_termination_msg,
    human_input_mode="NEVER",
)

agents.append(user_proxy)


# %%
# Groupchat activation
group_chat = GroupChat(
    agents=agents,
    messages=[],
    max_round=20,
    allowed_or_disallowed_speaker_transitions=speaker_transitions_dict,
    speaker_transitions_type="allowed",
)

# Create the manager/user/client that will ask for help
client = autogen.GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
    code_execution_config=False,
    is_termination_msg=is_termination_msg,
)

# %%
# Initiate chat
agents[0].initiate_chat(
    client,
    message="""
The client is a bank client. The client has questions. The graph and groupchat
represents a bank, its teams and the employees within. Help the client,
and direct the client to the appropriate team that can help them. E.g. if you
work in insurance and the client has a question about investments,
you should direct the client towards the investment team. 

Also, if you work on the right team to help the client, you must immediately give the right advice.

Here are the client's needs expressed from the client's point of view,
address these needs and explain your working:
    1. I am trying to get a new credit card. The bank offers two credit cards, A and B. Both credit cards have
    the same interest rate and other properties, except for the reward cash-back given. Credit card A
    gives cash back on groceries, and credit card B gives cash back on travel and plane tickets. I never travel or
    go on planes, in fact, I hate travelling and going on planes. I really enjoy cooking though,
    and I have a big family so I often go buy groceries and food for them. I think I need credit card B.
    If you think this is the right choice, please give me credit card B. Otherwise, give me a better credit card, 
    and explain why it is better.
    2. I am trying to purchase auto insurance for my vehicle. I drive a 2015 Toyota Corolla. Where do I go for that?
    Can you handle all the insurance paperwork for me please? Let me know the conditions and information about
    the insurance policy after it is finished. Just tell me the cost at the end. Thanks!
    3. I need to open another savings account for a family member, can we do that? Could you transfer me to the right department
    and have them complete that for me please?
    4. Turns out, I actually needed to invest a large sum of money, so I need to speak to the investments division.
    I want to buy $10000 worth of stocks, and put $50000 into mutual funds as well.""",
)
# %%
