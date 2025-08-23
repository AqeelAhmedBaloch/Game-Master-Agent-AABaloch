import os
import random
from dotenv import load_dotenv
import chainlit as cl
from openai import AsyncOpenAI
from agents import (Agent, Runner, OpenAIChatCompletionsModel, set_tracing_disabled, set_default_openai_api)

# ---------------- Env & SDK setup ---------------- #
load_dotenv()

# If you don't have an OpenAI key (using Gemini/OpenAI-compatible proxy), disable tracing.
set_tracing_disabled(True)

# Many non-OpenAI providers don't support Responses API — force Chat Completions shape globally.
# (We're also explicitly using OpenAIChatCompletionsModel below.)
set_default_openai_api("chat_completions")

# Configure Gemini (OpenAI-compatible) client
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)

# Single model adapter to reuse on agents
model_adapter = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=client,
)

# ---------------- Simple local tools ---------------- #
def roll_dice():
    return f"🎲 You rolled a {random.randint(1, 6)}!"

def generate_event():
    events = [
        "🌪️ A sudden storm surrounds you!",
        "🧟 A zombie crawls out of the ground!",
        "💎 You spot a mysterious glowing gem!",
        "🦴 A skeleton warrior blocks your path!",
    ]
    return random.choice(events)

# ---------------- Agents ---------------- #
narrator_agent = Agent(
    name="Narrator",
    instructions=(
        "You are the Narrator Agent. Describe the world, respond to player choices, "
        "and guide the adventure. Stay in character, build suspense, and ask questions "
        "to drive the story forward."
    ),
    model=model_adapter,
)

monster_agent = Agent(
    name="Monster",
    instructions=(
        "You are the Monster Agent. Engage the player in combat: describe enemies, "
        "attack moves, and let the player defend/attack. Stay in the combat phase "
        "until the player defeats or flees."
    ),
    model=model_adapter,
)

item_agent = Agent(
    name="Item Master",
    instructions=(
        "You are the Item Agent. Manage inventory, generate loot, assign weapons or "
        "healing items, and describe magical artifacts."
    ),
    model=model_adapter,
)

triage_agent = Agent(
    name="Triage Agent",
    instructions=(
        "Decide the correct agent for the user's input:\n"
        "- If it is about combat (attack/fight/run/monster), handoff to the Monster agent.\n"
        "- If it is about loot/items/inventory/chest/reward, handoff to the Item Master.\n"
        "- Otherwise, handoff to the Narrator.\n"
        "After handoff, the delegated agent should produce the final response."
    ),
    handoffs=[narrator_agent, monster_agent, item_agent],
    model=model_adapter,
)

# ---------------- Story Intro ---------------- #
def intro_story():
    return (
        "You stand at the edge of the haunted Everdark Forest.\n"
        "Type `roll` to roll a dice, `event` to trigger a random event, "
        "or begin your journey (e.g., 'go north', 'fight', 'search chest')."
    )

# ---------------- Chainlit Hooks ---------------- #
@cl.on_chat_start
async def start():
    await cl.Message("🎮 Welcome to the **Game Master Adventure** by Aqeel Ahmed Baloch!").send()
    await cl.Message(intro_story()).send()

@cl.on_message
async def handle_message(msg: cl.Message):
    user_input = msg.content.strip()

    try:
        if user_input.lower() in {"hi", "hello", "hey"}:
            await cl.Message(intro_story()).send()
            return

        if user_input.lower() == "roll":
            await cl.Message(roll_dice()).send()
            return

        if user_input.lower() == "event":
            await cl.Message(generate_event()).send()
            return

        # ✅ Run the workflow starting from triage_agent; handoffs are automatic.
        result = await Runner.run(triage_agent, input=user_input)

        # result.final_output is the final text from the last agent in the chain.
        output_text = result.final_output or "✅ Done."
        await cl.Message(output_text).send()

    except Exception as e:
        await cl.Message(f"❌ Error:\n{str(e)}").send()
