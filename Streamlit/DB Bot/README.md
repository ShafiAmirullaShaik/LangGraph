# 🗄️ DB Bot — SQLite Persistent Chatbot

A **real-time streaming chatbot** with **SQLite-backed persistence** built with LangGraph + Streamlit. Unlike the in-memory STM Bot, this bot stores all conversation history in a local SQLite database — so your chats survive app restarts.

---

## 📖 Table of Contents

- [What is DB Bot?](#-what-is-db-bot)
- [Why SQLite Persistence?](#-why-sqlite-persistence)
- [How It Works](#-how-it-works)
- [File Breakdown](#-file-breakdown)
- [MemorySaver vs SqliteSaver](#-memorysaver-vs-sqlitesaver)
- [How to Run](#-how-to-run)
- [How to Test](#-how-to-test)
- [Tech Stack](#-tech-stack)

---

## 🤔 What is DB Bot?

DB Bot is a Streamlit-based chatbot that combines:
- ⚡ **Token-by-token streaming** — responses appear word by word in real time
- 🗄️ **SQLite persistence** — conversation history saved to a local `chatbot.db` file
- 🧵 **Multi-thread support** — create and switch between multiple conversations
- 🧠 **Cross-session memory** — conversations persist even after restarting the app

```
STM Bot (Module 6)      → MemorySaver   → conversations lost on restart
Streaming Bot (Module 7) → MemorySaver   → conversations lost on restart
DB Bot (Module 9)        → SqliteSaver   → conversations saved permanently ✅
```

---

## 💡 Why SQLite Persistence?

| Feature | MemorySaver (In-Memory) | SqliteSaver (SQLite) |
|---------|------------------------|---------------------|
| Storage | Python dict in RAM | Local `.db` file on disk |
| Survives restart | ❌ Lost when app stops | ✅ Persists across restarts |
| Thread recovery | ❌ Threads disappear | ✅ All threads restored on startup |
| Setup complexity | None | Minimal — just `sqlite3.connect()` |
| Production-ready | ❌ Dev/testing only | ✅ Suitable for single-user production |
| Scalability | Limited by RAM | Limited by disk space |

> 💡 **Key insight:** Switching from `MemorySaver` to `SqliteSaver` requires changing only **2 lines of code** — the import and the checkpointer initialization. The rest of the LangGraph logic remains identical.

---

## ⚙️ How It Works

### Architecture Overview

```
User types message
        │
        ▼
┌─────────────────────┐
│   st.chat_input()   │    ← Streamlit captures input
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│   app.stream()      │    ← LangGraph streams the graph
│   stream_mode=      │
│   "messages"        │    ← Token-by-token mode
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  ai_only_stream()   │    ← Generator yields only AI tokens
│  yield token ───────────→  st.write_stream()
│                     │      renders each token live
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  SqliteSaver auto-  │    ← Checkpoint saved to chatbot.db
│  saves checkpoint   │
└─────────────────────┘
```

### Thread Management Flow

```
App starts
    │
    ▼
┌──────────────────────┐
│  get_all_threads()   │    ← Reads all thread IDs from SQLite
│  from chatbot.db     │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Sidebar shows all   │    ← Previous conversations listed
│  previous threads    │
└──────────┬───────────┘
           ▼
   User clicks a thread
           │
           ▼
┌──────────────────────┐
│  load_conversation() │    ← app.get_state() reads from SQLite
│  restores messages   │
└──────────────────────┘
```

---

## 📁 File Breakdown

### `app.py` — LangGraph Backend

| Component | What it does |
|-----------|-------------|
| `ChatBot` state | `TypedDict` with `messages` list using `add_messages` reducer |
| `chat_node()` | Sends all messages to the LLM (`llama-3.3-70b-versatile`), returns response |
| `sqlite3.connect()` | Creates/opens `chatbot.db` with `check_same_thread=False` for Streamlit compatibility |
| `SqliteSaver` | Checkpointer — persists state to SQLite after each graph run |
| `app` | Compiled graph: `START → chat_node → END` |
| `get_all_threads()` | Iterates all checkpoints in SQLite and returns unique thread IDs |

#### Key Code — SqliteSaver Setup

```python
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

# Connect to SQLite (creates chatbot.db if it doesn't exist)
conn = sqlite3.connect("chatbot.db", check_same_thread=False)

# Use SqliteSaver instead of MemorySaver
checkpointer = SqliteSaver(conn=conn)

# Compile graph with persistent checkpointer
app = graph.compile(checkpointer=checkpointer)
```

#### Key Code — Thread Recovery

```python
def get_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)
```

> `checkpointer.list(None)` iterates over **all** checkpoints in the database. We extract unique `thread_id` values to reconstruct the sidebar thread list on app restart.

---

### `bot.py` — Streamlit Frontend

| Section | What it does |
|---------|-------------|
| **Utility Functions** | `generate_thread_id()`, `reset_chat()`, `add_thread()`, `load_conversation()` |
| **Session Setup** | Initializes `message_history`, `thread_id`, and `chat_threads` from SQLite |
| **Custom CSS** | Gradient sidebar, styled buttons with hover effects, thread highlighting |
| **Sidebar UI** | "✨ New Chat" button + conversation thread list |
| **Main Chat Area** | Displays chat history, empty state prompt, and chat input |
| **Streaming** | `ai_only_stream()` generator yields AI tokens to `st.write_stream()` |

#### Key Code — Loading Saved Conversations

```python
def load_conversation(thread_id):
    state = app.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])
```

#### Key Code — Restoring Threads on Startup

```python
if 'chat_threads' not in st.session_state:
    existing_threads = get_all_threads()
    st.session_state['chat_threads'] = {
        tid: f'Chat {i}' for i, tid in enumerate(existing_threads, start=1)
    }
```

> On first load, the app reads all thread IDs from `chatbot.db` and populates the sidebar — even if the app was previously closed.

---

## 🔄 MemorySaver vs SqliteSaver

This is the **key difference** between the STM/Streaming bots and the DB Bot:

```python
# ❌ STM Bot / Streaming Bot — In-memory (lost on restart)
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()
```

```python
# ✅ DB Bot — SQLite persistence (survives restart)
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

conn = sqlite3.connect("chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
```

| | MemorySaver | SqliteSaver |
|---|---|---|
| **Import** | `from langgraph.checkpoint.memory import MemorySaver` | `from langgraph.checkpoint.sqlite import SqliteSaver` |
| **Setup** | `MemorySaver()` | `SqliteSaver(conn=sqlite3.connect("chatbot.db"))` |
| **Storage** | RAM (Python dict) | Disk (`chatbot.db` file) |
| **Thread recovery** | ❌ Not possible | ✅ `checkpointer.list(None)` |
| **Data after restart** | ❌ Gone | ✅ Still there |
| **`check_same_thread`** | N/A | Must be `False` for Streamlit (multi-threaded) |

---

## ▶️ How to Run

```powershell
# Make sure you're in the project root with the virtual environment activated
.\langvenv\Scripts\Activate.ps1

# Navigate to the DB Bot folder and run
cd "Streamlit/DB Bot"
streamlit run bot.py
```

> Make sure your `GROQ_API_KEY` is set in the `.env` file in the project root.

---

## 🧪 How to Test

### Test 1: Verify Streaming
1. Type any message (e.g., "Explain what databases are")
2. You should see the response **appear word by word** — not all at once
3. Longer responses make the streaming effect more obvious

### Test 2: Verify Memory Within a Session
1. Say: "My name is Alex"
2. Then ask: "What's my name?"
3. The bot should answer "Alex" — proving within-session memory works

### Test 3: Verify Persistence Across Restarts
1. Have a conversation with the bot
2. **Stop the Streamlit app** (Ctrl+C in terminal)
3. **Restart the app** (`streamlit run bot.py`)
4. Your previous conversations should appear in the sidebar ✅
5. Click on a thread — the full conversation history should load

### Test 4: Thread Isolation
1. Tell the bot your name in Thread 1
2. Click **✨ New Chat** to create a new thread
3. Ask "What's my name?" — the bot should NOT know (different thread)

### Test 5: Verify Database File
1. After chatting, check the `DB Bot` folder
2. You should see a `chatbot.db` file
3. You can inspect it with any SQLite viewer to see the stored checkpoints

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| LangGraph | Graph-based workflow + `app.stream()` |
| LangChain-Groq | Llama 3.3 70B LLM access |
| Streamlit | Web UI + `st.write_stream()` |
| SqliteSaver | SQLite-based checkpointing for persistent memory |
| SQLite3 | Lightweight local database for storing conversations |
| Python Generators | `yield` tokens one at a time for real-time display |
