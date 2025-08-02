# 🧙‍♂️ Game Master Agent

**Game Master Agent** is an AI-powered, text-based fantasy adventure game where a player can immerse themselves in interactive storytelling. The system is built using [Chainlit](https://www.chainlit.io/), and leverages multiple autonomous agents to deliver a dynamic role-playing experience.

## 🎮 Features

- 📜 **Narrator Agent**: Guides the story, presents scenarios, and gives the player choices.
- 🎲 **Dice Agent**: Simulates dice rolls to determine random outcomes.
- ⚔️ **Game Logic Agent**: Controls combat, events, and overall gameplay logic.
- 🧠 **Multi-Agent Collaboration**: Agents communicate with each other to progress the story.
- 🔧 **Tool Integration**:
  - `roll_dice()`: Random event generation
  - `generate_event()`: Creates scenarios for the player
- 🧪 Built with **OpenAI Agent SDK** and **Chainlit UI** for a seamless interactive experience.

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- Node.js (for frontend Chainlit UI, optional)

### 1. Clone the Repository

```bash
git clone https://github.com/AqeelAhmedBaloch/Game-Master-Agent-AABaloch.git
cd Game-Master-Agent-AABaloch
