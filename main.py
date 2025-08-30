import os
import chainlit as cl
from typing import cast
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, RunConfig,handoff, OpenAIChatCompletionsModel, RunContextWrapper


load_dotenv()

# 🛠 Define tools using Agentic AI SDK's @tool decorator

def setup_config():
    # External Client
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url=os.getenv("BASE_URL"),
    )

    model = OpenAIChatCompletionsModel(
        model="gemini-1.5-flash",
        openai_client=external_client,
    )

    config = RunConfig(
        model=model,
        model_provider=external_client, 
        tracing_disabled=True
        )

    # 🎭 Agents
    narrator_agent = Agent(
        name="narrator_agent",
        instructions="You narrate the adventure and guide the player through the story.",
        handoff_description="Handles story narration and progress.",
        model=model
    )

    monster_agent = Agent(
        name="monster_agent",
        instructions="You control monsters during combat, describe attacks and outcomes.",
        handoff_description="Handles combat scenarios with enemies.",
        model=model
    )

    item_agent = Agent(
        name="item_agent",
        instructions="You manage inventory, give rewards, and describe found items.",
        handoff_description="Handles items, treasures, and inventory events.",
        model=model
    )

    # 🎮 Game Master Agent (triage)
    triage_agent = Agent(
        name="triage_agent",
        instructions=(
            "You are the Game Master of a fantasy adventure. Use the given tools to roll dice and "
            "generate random events. Dynamically hand off control to the relevant agent based on "
            "the game phase (narration, combat, inventory)."
        ),
        handoffs=[
                  (item_agent),
                  (monster_agent),
                  (narrator_agent)
                ],
        model=model
    )

    return triage_agent, config


@cl.on_chat_start
async def start():
    triage_agent, config = setup_config()
    cl.user_session.set("triage_agent", triage_agent)
    cl.user_session.set("config", config)
    cl.user_session.set("chat_history", [])
    await cl.Message(content="🎮 Welcome to the Fantasy Adventure Game! Type 'start' to begin your quest.").send()

@cl.on_message
async def main(message: cl.Message):
    """Main handler for incoming messages."""
    msg = cl.Message(content="🎲 Thinking...")
    await msg.send()

    triage_agent = cast(Agent, cl.user_session.get("triage_agent"))
    config = cast(RunConfig, cl.user_session.get("config"))
    history = cl.user_session.get("chat_history") or []

    history.append({"role": "user", "content": message.content})

    # 🏹 Run the Triage Agent
    result = await Runner.run(triage_agent, history, run_config=config)

    response_content = result.final_output
    msg.content = response_content
    await msg.update()

    history.append({"role": "assistant", "content": response_content})
    cl.user_session.set("chat_history", history)

    print(f"Chat history: {history}")  # Debugging line to check chat history
    