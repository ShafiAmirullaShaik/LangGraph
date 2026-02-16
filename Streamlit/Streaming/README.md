# ⚡ Streaming Chat Bot

A real-time **token-by-token streaming chatbot** built with LangGraph + Streamlit. Instead of waiting for the entire AI response, tokens appear on screen as the LLM generates them — just like ChatGPT.

---

## 📖 Table of Contents

- [What is Streaming?](#-what-is-streaming)
- [Why Streaming?](#-why-streaming)
- [What is a Generator?](#-what-is-a-generator)
- [How Streaming Works in This Project](#-how-streaming-works-in-this-project)
- [File Breakdown](#-file-breakdown)
- [invoke() vs stream() — The Key Difference](#-invoke-vs-stream--the-key-difference)
- [How to Run](#-how-to-run)
- [How to Test](#-how-to-test)

---

## 🤔 What is Streaming?

In LLMs, streaming means the model starts sending tokens (words) **as soon as they're generated**, instead of waiting for the entire response to be ready before returning it.

```
Without Streaming:
User sends message → [........waiting........] → Full response appears at once

With Streaming:
User sends message → "I" → "think" → "that" → "is" → "a" → "great" → "question" → "!"
                     ↑ tokens appear one by one in real time
```

---

## 💡 Why Streaming?

1. **Faster response time** — low drop-off rates, users see output immediately
2. **Mimics human-like conversation** — builds trust, feels alive and keeps the user engaged
3. **Important for Multi-modal UIs** — interleave text, images, tool outputs
4. **Better UX for long output** such as code or essays
5. **You can cancel midway** saving tokens (and money!)
6. **You can interleave UI updates** — e.g., show "thinking...", then show tool results

---

## 🔁 What is a Generator?

A **generator** is a special Python function that **produces values one at a time**, pausing between each one, instead of computing everything at once and returning a list.

### Regular Function vs Generator

```python
# ❌ Regular function — computes ALL values, then returns a list
def get_numbers():
    result = []
    for i in range(5):
        result.append(i)
    return result                # returns [0, 1, 2, 3, 4] all at once

numbers = get_numbers()          # everything is in memory at once
```

```python
# ✅ Generator function — yields values ONE AT A TIME
def get_numbers():
    for i in range(5):
        yield i                  # pauses here, gives one value, waits for next call

numbers = get_numbers()          # nothing computed yet!
next(numbers)                    # → 0 (computes just this one)
next(numbers)                    # → 1 (computes the next one)
next(numbers)                    # → 2
```

### How `yield` Works

| Keyword | What it does |
|---------|-------------|
| `return` | Sends back **one value** and the function **ends forever** |
| `yield` | Sends back **one value** and the function **pauses** — it remembers where it stopped and continues from there on the next call |

### Why Generators Matter for Streaming

Think of it like a **conveyor belt** vs a **delivery truck**:

```
Delivery Truck (return):
    Factory makes ALL items → loads them ALL on truck → delivers everything at once
    Problem: you wait until EVERYTHING is ready

Conveyor Belt (yield):
    Factory makes item 1 → puts it on belt → you grab it
    Factory makes item 2 → puts it on belt → you grab it
    ...no waiting!
```

For LLM streaming, each `yield` passes **one token** (word/chunk) to Streamlit, which immediately displays it on screen. The user sees text appearing word by word instead of staring at a spinner.

---

## ⚙️ How Streaming Works in This Project

### The Complete Flow

```
User types message
        │
        ▼
┌─────────────────────┐
│   st.chat_input()   │    ← Streamlit captures input
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│   stream_response() │    ← Our generator function
│                     │
│   app.stream(       │    ← LangGraph streams the graph
│     stream_mode=    │
│     "messages"      │    ← Token-by-token mode
│   )                 │
│                     │
│   for each chunk:   │
│     yield token ──────────→  st.write_stream()
│                     │        renders each token
│                     │        on screen instantly
└─────────────────────┘
           │
           ▼
    LangGraph auto-saves
    checkpoint (full response
    saved for memory)
```

### Step-by-Step Breakdown

#### Step 1: User sends a message
```python
if user_input := st.chat_input("Type your message..."):
```
Streamlit captures what the user typed.

#### Step 2: We call our generator
```python
with st.chat_message("assistant", avatar="🤖"):
    ai_response = st.write_stream(stream_response(user_input, config))
```
`st.write_stream()` takes a **generator** and renders each yielded value in real time.

#### Step 3: The generator streams from LangGraph
```python
def stream_response(user_message: str, config: dict):
    for msg_chunk, metadata in app.stream(
        {"messages": [HumanMessage(content=user_message)]},
        config=config,
        stream_mode="messages",
    ):
        if msg_chunk.content and metadata["langgraph_node"] == "chat_node":
            yield msg_chunk.content
```

Let's break this down line by line:

| Line | What it does |
|------|-------------|
| `app.stream(...)` | Runs the LangGraph graph but instead of returning everything at once, it **streams events** as they happen |
| `stream_mode="messages"` | Tells LangGraph to stream at the **message token level** — each chunk is a small piece of the AI response (a word or a few characters) |
| `for msg_chunk, metadata in ...` | Loops through each streamed chunk. `msg_chunk` is the token, `metadata` tells us which node produced it |
| `metadata["langgraph_node"] == "chat_node"` | Filter: only yield chunks from the AI chat node (ignores system/human messages being echoed) |
| `yield msg_chunk.content` | **Gives one token to Streamlit** and pauses — Streamlit immediately shows it on screen |

#### Step 4: `st.write_stream()` renders tokens live
`st.write_stream()` does three things:
1. Calls `next()` on our generator repeatedly
2. Each time it gets a token, it **appends it to the screen**
3. When the generator is exhausted (no more tokens), it **returns the full concatenated string**

```python
ai_response = st.write_stream(stream_response(user_input, config))
# ai_response is now the complete response string like "I think that is a great question!"
```

#### Step 5: Save to history
```python
st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
```
The complete response is saved for displaying on future reruns.

---

## 📁 File Breakdown

### `Bot.py` — LangGraph Backend

| Component | What it does |
|-----------|-------------|
| `ChatBot` state | Holds `messages` list with `add_messages` reducer |
| `chat_node` | Sends all messages to the LLM, returns the response |
| `MemorySaver` | Checkpointer — saves state after each graph run |
| `app` | Compiled graph: `START → chat_node → END` |

The graph is the same as the STM Bot. Streaming happens at the **Streamlit layer** — `app.stream()` tells LangGraph to send tokens as they're generated instead of waiting for the full response.

### `app.py` — Streamlit Frontend

| Section | What it does |
|---------|-------------|
| Page Config & CSS | Sets up the UI with custom styling and gradient sidebar |
| Session State | Manages `thread_id`, `chat_history`, `all_threads` |
| Sidebar | Thread management, "How it works" info, tech stack |
| Chat History | Displays previous messages from `st.session_state` |
| `stream_response()` | **Generator** — yields tokens one by one from LangGraph |
| Chat Input | Captures user input → calls `st.write_stream()` → saves response |

---

## 🔄 `invoke()` vs `stream()` — The Key Difference

This is the **only code change** between the STM Bot and the Streaming Bot:

```python
# ❌ STM Bot — invoke() waits for complete response
with st.spinner("Thinking..."):
    result = app.invoke(
        {"messages": [HumanMessage(content=user_input)]},
        config=config,
    )
    ai_response = result["messages"][-1].content
st.markdown(ai_response)
```

```python
# ✅ Streaming Bot — stream() yields tokens in real time
def stream_response(user_message, config):
    for msg_chunk, metadata in app.stream(
        {"messages": [HumanMessage(content=user_message)]},
        config=config,
        stream_mode="messages",
    ):
        if msg_chunk.content and metadata["langgraph_node"] == "chat_node":
            yield msg_chunk.content

ai_response = st.write_stream(stream_response(user_input, config))
```

| | `invoke()` | `stream()` |
|---|---|---|
| **Returns** | Complete result after graph finishes | Token-by-token chunks as they're generated |
| **User sees** | Spinner → full text appears at once | Text appears word by word in real time |
| **UX** | Feels slow, especially for long responses | Feels fast and responsive |
| **Memory** | Checkpoint saved after invoke | Checkpoint saved after stream completes |
| **Under the hood** | Runs graph, collects all output, returns | Runs graph, `yield`s each LLM token via generator |

---

## ▶️ How to Run

```powershell
# Make sure you're in the Streaming folder
cd "Streamlit/Streaming"

# Run the Streamlit app
streamlit run app.py
```

> Make sure your virtual environment is activated and `GROQ_API_KEY` is set in the `.env` file.

---

## 🧪 How to Test

### Test 1: Verify Streaming
1. Type any message (e.g., "Explain what Python is")
2. You should see the response **appear word by word** — not all at once
3. Longer responses make the streaming effect more obvious

### Test 2: Verify Memory Still Works
1. Say: "My name is Alex"
2. Then ask: "What's my name?"
3. The bot should answer "Alex" — proving memory works even with streaming

### Test 3: Thread Isolation
1. Tell the bot your name in Thread 1
2. Click **➕ New Conversation** to create Thread 2
3. Ask "What's my name?" — the bot should NOT know (different thread)

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| LangGraph | Graph-based workflow + `app.stream()` |
| LangChain-Groq | Llama 3.3 70B LLM access |
| Streamlit | Web UI + `st.write_stream()` |
| MemorySaver | In-memory checkpointing for conversation memory |
| Python Generators | `yield` tokens one at a time to enable real-time display |
