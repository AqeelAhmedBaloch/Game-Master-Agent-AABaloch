import os
import random
from dotenv import load_dotenv
import chainlit as cl
from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, Agent

# Load environment variables
load_dotenv()

# Configure Gemini Proxy as OpenAI-compatible client
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url=os.getenv("BASE_URL")
)

# Define Gemini model
model_name = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=client
)

# -------- Tools -------- #
def roll_dice():
    return f"🎲 You rolled a {random.randint(1, 6)}!"

def generate_event():
    events = [
        "🌪️ A sudden storm surrounds you!",
        "🧟 A zombie crawls out of the ground!",
        "💎 You spot a mysterious glowing gem!",
        "🦴 A skeleton warrior blocks your path!"
    ]
    return random.choice(events)

# -------- Agents -------- #
narrator_agent = Agent(
    name="Narrator",
    instructions=(
        "You are the Narrator Agent. Describe the world, respond to player choices, and guide the adventure. "
        "Stay in character and build suspense. Ask questions to drive the story forward."
    ),
    model=model_name
)

monster_agent = Agent(
    name="Monster",
    instructions=(
        "You are the Monster Agent. Engage the player in combat, describe enemies, attack moves, and allow the player to defend or attack. "
        "Always stay in the combat phase until the player defeats or flees from the monster."
    ),
    model=model_name
)

item_agent = Agent(
    name="Item Master",
    instructions=(
        "You are the Item Agent. Manage the player's inventory, generate loot, assign weapons or healing items, and describe magical artifacts."
    ),
    model=model_name
)

# -------- Story Intro -------- #
def intro_story():
    return (
        "You stand at the edge of the haunted Everdark Forest.\n"
        "Type `roll` to roll a dice, `event` to trigger a random event, or begin your journey (e.g., 'go north', 'fight', 'search chest')."
    )

# -------- Agent Selector Based on Input -------- #
def select_agent(user_input):
    if any(word in user_input for word in ["attack", "fight", "run", "monster"]):
        return monster_agent
    elif any(word in user_input for word in ["loot", "inventory", "chest", "item", "reward"]):
        return item_agent
    else:
        return narrator_agent

# -------- Chainlit Start -------- #
@cl.on_chat_start
async def start():
    await cl.Message("🎮 Welcome to the **Game Master Adventure** by Aqeel Ahmed Baloch!").send()
    await cl.Message(intro_story()).send()

# -------- Message Handler -------- #
@cl.on_message
async def handle_message(msg: cl.Message):
    user_input = msg.content.strip().lower()

    try:
        if user_input in ["hi", "hello", "hey"]:
            await cl.Message(intro_story()).send()

        elif user_input == "roll":
            await cl.Message(roll_dice()).send()

        elif user_input == "event":
            await cl.Message(generate_event()).send()

        else:
            agent = select_agent(user_input)
            completion = await client.chat.completions.create(
                model=agent.model.model,
                messages=[
                    {"role": "system", "content": agent.instructions},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=1024
            )
            await cl.Message(completion.choices[0].message.content).send()

    except Exception as e:
        await cl.Message(f"❌ Error:\n{str(e)}").send()
