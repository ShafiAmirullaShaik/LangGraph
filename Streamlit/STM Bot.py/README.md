# 🧠 STM Bot — Short-Term Memory Chatbot

A chatbot that **remembers your conversation** using LangGraph's persistence and checkpointing.

---

## 📁 Project Files

### `Bot.py` — The Brain (Backend)

This file builds the **LangGraph graph** — the engine behind the chatbot.

#### Step-by-step breakdown:

```
1. Load API Key         →  Reads GROQ_API_KEY from the .env file
2. Create the LLM       →  Sets up Llama 3.3 70B via Groq
3. Define the State      →  What data the graph carries around
4. Define the Node       →  The function that talks to the LLM
5. Build the Graph       →  Connect nodes with edges (START → chatbot → END)
6. Compile with Memory   →  Attach MemorySaver so it remembers conversations
```

#### Key pieces explained:

| Code | What it does | Why it matters |
|---|---|---|
| `ChatBot(TypedDict)` | Defines the state — a dict with a `messages` list | This is the data that flows through the graph |
| `Annotated[List, add_messages]` | Uses `add_messages` as a **reducer** | Instead of replacing messages, it **appends** new ones — this is what builds up chat history |
| `chat_node(state)` | Takes all messages, sends them to the LLM, returns the response | The LLM sees the **full** conversation every time, so it has context |
| `MemorySaver()` | Stores checkpoints (state snapshots) in memory (RAM) | This is what makes the bot "remember" between messages |
| `graph.compile(checkpointer=...)` | Builds the final app with persistence enabled | Without this, every message starts from scratch |

#### The graph is super simple:

```
START ──→ chat_node ──→ END
```

One node, one job: take messages in → get LLM response → return it.

---

### `app.py` — The Face (Frontend / UI)

This file creates the **Streamlit web interface**. It imports the `app` (compiled graph) from `Bot.py` and wraps it in a beautiful chat UI.

#### Step-by-step breakdown:

```
1. Import Bot            →  Gets the compiled LangGraph app from Bot.py
2. Page Config           →  Sets title, icon, and layout
3. Custom CSS            →  Gradient sidebar, styled chat bubbles, badges
4. Session State         →  Tracks thread_id, chat history, and threads
5. Sidebar               →  Thread info, "New Conversation" button, thread switcher
6. Chat Display          →  Shows message history (or empty state if new)
7. Chat Input            →  Takes user input, calls LangGraph, shows response
```

#### Key pieces explained:

| Code | What it does | Why it matters |
|---|---|---|
| `from Bot import app` | Imports the compiled LangGraph graph | Keeps backend and frontend separate |
| `st.session_state` | Streamlit's way of keeping data between reruns | Stores chat history, thread ID, etc. without losing them on page refresh |
| `thread_id` | A unique ID for each conversation | Same `thread_id` = bot remembers you. New `thread_id` = fresh start |
| `app.invoke({"messages": [...]}, config)` | Sends a message to LangGraph | The `config` with `thread_id` tells LangGraph WHICH conversation to load/save |
| `result["messages"][-1].content` | Gets the AI's response | The last message in the list is always the latest AI reply |
| `st.chat_message()` | Streamlit's built-in chat bubble component | Makes it look like a real chat app |
| `st.rerun()` | Refreshes the page after a new message | Ensures the chat history display is up to date |

#### Thread switching:

When you click a thread in the sidebar, the app:
1. Reads the checkpoint from LangGraph: `app.get_state(config)`
2. Rebuilds the chat history from the saved messages
3. Displays them in the UI

This means **even if you switch threads, your old conversations are restored from LangGraph's memory!**

---

## 🧪 How to Test Memory

1. **Run the app:** `streamlit run app.py`
2. **Tell the bot your name:** `"My name is Syed"`
3. **Ask it later:** `"What is my name?"`  → It remembers! ✅
4. **Click "➕ New Conversation"** in the sidebar
5. **Ask again:** `"What is my name?"`  → It doesn't know! ❌ (different thread)
6. **Switch back** to Thread 1 → Your old conversation is restored

---

## 🔑 The Big Idea (for Beginners)

```
Without Persistence:          With Persistence:
┌─────────────┐               ┌─────────────┐
│ You: Hi     │               │ You: Hi     │
│ Bot: Hello! │               │ Bot: Hello! │
└─────────────┘               │             │
                              │ You: Name?  │
┌─────────────┐               │ Bot: Syed!  │  ← Remembers!
│ You: Name?  │               │             │
│ Bot: ???    │  ← Forgot!    │ You: Bye    │
└─────────────┘               │ Bot: Bye!   │
                              └─────────────┘
Each invoke() is isolated      All invoke() share the
                               same checkpoint (memory)
```

**Three things make memory work:**
1. **`MemorySaver`** — saves state after every step
2. **`thread_id`** — identifies which conversation to save/load
3. **`add_messages` reducer** — appends messages instead of replacing them

---

## ▶️ How to Run

```bash
# Make sure you're in the STM Bot.py folder
cd "c:\LAE\Learnings\LangGraph\Streamlit\STM Bot.py"

# Activate the virtual environment
..\..\..\langvenv\Scripts\activate

# Run the Streamlit app
streamlit run app.py
```

## 📦 Requirements

- `langchain`, `langchain-core`, `langchain-groq`
- `langgraph`
- `streamlit`
- `python-dotenv`
- A `GROQ_API_KEY`
