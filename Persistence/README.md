# 🧠 LangGraph Persistence & Checkpointing

Understanding how LangGraph saves and restores graph state using **Persistence** and **Checkpoints**.

---

## 📌 What is Persistence?

Persistence means **saving the graph's state** so it survives across multiple `.invoke()` calls. Without it, every call starts from a blank slate.

### Key Components

| Component | Purpose |
|---|---|
| **Checkpoint** | A snapshot of the graph's state saved automatically after each node runs |
| **InMemorySaver** | A checkpointer that stores checkpoints in RAM (use `SqliteSaver` / `PostgresSaver` for production) |
| **thread_id** | Identifies a conversation — same `thread_id` = same memory, different `thread_id` = fresh state |
| **add_messages** | A reducer that **appends** new messages instead of replacing them — this builds conversation history |

---

## 📓 What's in the Notebook

### 1️⃣ Joke Generator with Checkpointing
A simple 2-node graph (`generate_joke` → `explain_joke`) compiled with `InMemorySaver` to demonstrate basic checkpointing.

```
START → generate_joke → explain_joke → END
```

**State:**
```python
class JokeState(TypedDict):
    topic: str
    joke: str
    explanation: str
```

**Key takeaway:** After `app.invoke()`, the full state (topic + joke + explanation) is saved as a checkpoint and can be retrieved with `app.get_state(config)`.

---

### 2️⃣ State Inspection — `get_state()` & `get_state_history()`

| Method | What it returns |
|---|---|
| `app.get_state(config)` | The **latest** checkpoint for a thread |
| `app.get_state_history(config)` | **All** checkpoints for a thread (one per node execution) |

Each `StateSnapshot` contains:
- `values` — the state dict at that point
- `next` — which node runs next (empty if graph is done)
- `config` — includes `thread_id` and `checkpoint_id`
- `metadata` — source (`loop`/`input`/`update`) and step number

**Multiple threads:** Using different `thread_id` values (`'1'` for cats, `'2'` for Buffalo) keeps conversations completely separate.

---

### 3️⃣ Short-Term Memory Chatbot

A chatbot that **remembers previous messages** within the same thread using `add_messages` reducer + checkpointing.

```
START → chatbot → END
```

**How it works:**
```
invoke() with thread_id "1":
  1. Load checkpoint → old messages restored
  2. add_messages reducer appends new HumanMessage
  3. LLM sees FULL history → generates response
  4. New checkpoint saved with all messages
```

**Try this to see memory in action:**
```
You: My name is Alice       → Bot greets you
You: What is my name?       → Bot remembers "Alice" ✅
Type 'new' → switches to Thread 2
You: What is my name?       → Bot doesn't know ❌ (different thread!)
```

---

### 4️⃣ Fault Tolerance

Demonstrates how checkpointing enables **crash recovery** — if the graph is interrupted mid-execution, it resumes from the last completed step.

```
START → step_1 → step_2 (crash here!) → step_3 → END
```

**Flow:**
1. Run the graph — `step_1` completes, `step_2` is interrupted (simulated crash)
2. Re-run with `graph.invoke(None, config)` — graph **skips** `step_1` and resumes from `step_2`
3. The `None` input tells LangGraph to resume from the last checkpoint

**Key takeaway:** Passing `None` as input + same `thread_id` = resume from where it left off.

---

### 5️⃣ Time Travel

Go back to a **previous checkpoint** and re-run the graph from that point.

**How:**
1. Get history: `app.get_state_history(config)` → find the `checkpoint_id` you want
2. Invoke from that point: `app.invoke(None, {"configurable": {"thread_id": "1", "checkpoint_id": "<id>"}})`

This creates a **new branch** in the checkpoint history — the original history is preserved.

---

### 6️⃣ Updating State

Manually modify the state at a specific checkpoint using `update_state()`.

```python
app.update_state(
    {"configurable": {"thread_id": "1", "checkpoint_id": "<id>"}},
    {"topic": "samosa"}  # Override the topic
)
```

This creates a **new checkpoint** with `source: "update"` (instead of `"loop"`), then you can invoke from it to continue the graph with the modified state.

---

## 🔑 Benefits of Persistence

| Benefit | Example |
|---|---|
| **Memory & Context** | A support bot remembering a user's order ID from yesterday |
| **Fault Tolerance** | Resuming a 10-step process from step 6 after a server crash |
| **Human-in-the-loop** | Pausing for manager approval before publishing a report |
| **Time Travel** | Rewinding to step 4, modifying input, and re-running to debug |
| **Long-running Workflows** | A hiring assistant that follows up 3 days after an interview |

---

## 🛠️ Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
GROQ_API_KEY=your_key_here
```

## 📦 Dependencies

- `langchain`, `langchain-core`, `langchain-community`
- `langchain-groq` (LLM provider)
- `langgraph` (graph framework with persistence)
- `python-dotenv` (env variable loading)
- `pydantic`
