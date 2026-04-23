# AGENT-FUNDAMENTALS.md
## Day 1 — Agent Foundations & Message-Based Communication

---

## What is an AI Agent?

An AI agent is a system that perceives its environment, reasons about it,
and takes actions to achieve a goal — autonomously, without step-by-step
human instruction.

### Agent vs Chatbot vs Pipeline

| Type      | Description                                              | Example                        |
|-----------|----------------------------------------------------------|--------------------------------|
| Chatbot   | Responds to messages, no memory, no goals                | Basic FAQ bot                  |
| Pipeline  | Fixed sequence of steps, no decision-making              | ETL data pipeline              |
| AI Agent  | Perceives → Reasons → Acts → loops, has role + memory    | ResearchAgent in this project  |

---

## The Perception → Reasoning → Action Loop

```
User Input (Perception)
       ↓
 LLM processes with system prompt (Reasoning)
       ↓
 Agent produces output / calls next agent (Action)
       ↓
 Output becomes next agent's input (loop continues)
```

---

## ReAct Pattern (Reason + Act)

ReAct = **Re**ason + **Act**

The agent first **thinks** about what to do (reasoning trace), then
**acts** on that reasoning (tool call or message output).

```
Thought: I need to find facts about X
Action:  Search / generate research
Observation: Here are the facts...
Thought: Now I should summarize
Action:  Produce summary
...
```

This is what separates agents from simple LLM calls — they chain
reasoning and action steps together.

---

## System Prompts for Role Isolation

Each agent in this project has a strict system prompt that locks it
into one job. This is called **role isolation** — an agent must not
do another agent's job.

| Agent           | Role                        | System Prompt Goal                        |
|-----------------|-----------------------------|-------------------------------------------|
| ResearchAgent   | Gather raw facts            | Output bullet points only, no summarizing |
| SummarizerAgent | Condense research           | 3-5 sentence summary, no new info         |
| AnswerAgent     | Craft final user response   | Friendly answer, no raw data              |

---

## Message Passing Protocol

Agents communicate by passing messages — the output of one agent
becomes the input of the next. This is the core of multi-agent systems.

```
User
 └──► ResearchAgent  (message: "Research topic X")
          └──► SummarizerAgent  (message: research output)
                    └──► AnswerAgent  (message: summary + original query)
                              └──► Final Answer to User
```

No agent talks directly to another — a relay proxy passes messages
between them, keeping conversations isolated.

---

## Memory Window

Each agent in this project uses a **memory window of 10**, meaning it
only sees the last 10 messages in its conversation history.

```python
MEMORY_WINDOW = 10
chat_history[-MEMORY_WINDOW:]
```

This prevents context overflow and keeps each agent focused on its
current task. This is **short-term memory** — it resets each run.

---

## Model Used

| Property       | Value                                      |
|----------------|--------------------------------------------|
| Model          | llama-3.3-70b-versatile                    |
| Provider       | Groq (cloud API — free, no credit card)    |
| Endpoint       | https://api.groq.com/openai/v1             |
| Internet       | Required (Groq cloud API)                  |
| GPU            | Not required (runs on Groq's hardware)     |
| Cost           | Free — Groq free tier                      |

---

## Project Structure

```
week9/day1/
├── agents/
│   ├── research_agent.py      # Gathers raw facts
│   ├── summarizer_agent.py    # Condenses facts into summary
│   └── answer_agent.py        # Crafts final user-facing answer
├── main.py                    # Orchestrates the 3-agent pipeline
├── requirements.txt           # Python dependencies
├── .env                       # Model config
└── AGENT-FUNDAMENTALS.md      # This file
```

---

## How to Run Day 1

### Prerequisites

```bash
# 1. Get a free Groq API key at https://console.groq.com
#    No credit card required — sign up and create an API key

# 2. Set your .env file (see Environment Config below)
```

### Run the project

```bash
# Navigate to project
cd ~/Documents/Training/Week9/day1

# Activate virtual environment
source venv/bin/activate

# Run the pipeline
python main.py
```

### Test individual agents

```bash
# Test ResearchAgent alone
python -c "
from agents.research_agent import get_research_agent
import autogen
agent = get_research_agent()
proxy = autogen.UserProxyAgent(name='Tester', human_input_mode='NEVER', max_consecutive_auto_reply=1, code_execution_config=False)
proxy.initiate_chat(agent, message='Research what AutoGen is', max_turns=1)
"
```

---

## Key Concepts Demonstrated

| Concept                    | How it's implemented                               |
|----------------------------|----------------------------------------------------|
| Role isolation             | Strict system_message per agent                    |
| Message passing            | UserProxyAgent relays output between agents        |
| Memory window              | chat_history[-10:] slice                           |
| ReAct pattern              | Research → Summarize → Answer chain                |
| Cloud LLM                  | Llama 3.3 70B via Groq API, free tier              |
| Chain-of-thought isolation | Each agent runs in its own separate chat session   |

---

## Dependencies

```
ag2==0.7.6          # AutoGen framework (supports Python 3.12+)
openai              # Required by AutoGen internally
python-dotenv       # Loads .env config
```

---

## Environment Config (.env)

```env
OPENAI_API_BASE=https://api.groq.com/openai/v1
OPENAI_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
```

- `OPENAI_API_BASE` points to Groq's OpenAI-compatible endpoint
- `OPENAI_API_KEY` is your free Groq API key from https://console.groq.com
- `MODEL_NAME` can also be `llama-3.1-8b-instant` (faster) or `gemma2-9b-it`