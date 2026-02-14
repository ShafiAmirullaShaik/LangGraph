# 🤖 Basic Chatbot

> A simple interactive chatbot built with **LangGraph** and **Groq LLM** that supports multi-turn conversations with memory.

---

## 📁 File

| File | Description |
|------|-------------|
| `ChatBot.py` | Interactive chatbot with conversation memory |

---

## 💡 What We Did

- Created a **stateful chatbot** that remembers the conversation history across multiple turns.
- Used `TypedDict` to define a `ChatBot` state that holds a list of messages (`HumanMessage`, `AIMessage`).
- Used `add_messages` as an **annotation reducer** — this tells LangGraph to **append** new messages to the list instead of replacing them.
- Built a single-node graph:
  ```
  START → chat_node → END
  ```
- The `chat_node` function takes all messages in the state, sends them to the **Groq LLM** (`llama-3.3-70b-versatile`), and returns the AI's response.
- Used **`MemorySaver`** as a checkpointer to persist conversation state across invocations (in-memory).
- Each conversation is identified by a unique `thread_id`, so the bot remembers what was said before.
- The bot runs in a `while True` loop — type your message and get a response. Type `exit`, `quit`, or `bye` to stop.

---

## 🔑 Key Concepts Learned

| Concept | What It Means |
|---------|---------------|
| **StateGraph** | The graph structure that defines how nodes are connected |
| **State (`TypedDict`)** | A shared data structure that holds the current context (messages) |
| **`add_messages` reducer** | Appends new messages to the list instead of overwriting |
| **MemorySaver** | In-memory checkpointer that enables conversation persistence |
| **`thread_id`** | Unique identifier for a conversation thread (enables multi-turn memory) |
| **`app.get_state()`** | Inspect the current state of the graph for debugging |

---

## 🔄 Graph Flow

```
┌───────┐      ┌───────────┐      ┌─────┐
│ START │ ───→ │ chat_node │ ───→ │ END │
└───────┘      └───────────┘      └─────┘
                    │
                    ▼
              Sends messages
              to Groq LLM &
              returns response
```

---

## ▶️ How to Run

```bash
# Activate virtual environment
.\langvenv\Scripts\Activate.ps1

# Run the chatbot
python "Basic Bot/ChatBot.py"
```

> **Note:** Make sure your `.env` file has the `GROQ_API_KEY` set.

---

## 📝 Sample Interaction

```
You: Hello!
Bot: Hello! How can I help you today?
--------------------------------------------------
You: What is Python?
Bot: Python is a high-level, interpreted programming language...
--------------------------------------------------
You: bye
Exiting chat. Goodbye!
```
