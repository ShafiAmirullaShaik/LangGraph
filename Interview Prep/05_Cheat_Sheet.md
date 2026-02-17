# ⚡ LangGraph — Cheat Sheet

> Your last-minute quick-reference card. Pin this, print this, love this.

---

## 🔧 Essential Imports

```python
# Core LangGraph
from langgraph.graph import StateGraph, START, END
from langgraph.graph import add_messages

# State types
from typing import TypedDict, Annotated
import operator

# Checkpointing
from langgraph.checkpoint.memory import MemorySaver          # Dev
# from langgraph.checkpoint.sqlite import SqliteSaver        # Small prod
# from langgraph.checkpoint.postgres import PostgresSaver     # Large prod

# LangChain Messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# LLM
from langchain_groq import ChatGroq

# Structured Output
from pydantic import BaseModel, Field

# Environment
from dotenv import load_dotenv
load_dotenv()
```

---

## 📐 State Definition Patterns

```python
# Basic state
class State(TypedDict):
    query: str
    result: str

# State with reducer (for parallel workflows)
class State(TypedDict):
    scores: Annotated[list[int], operator.add]  # Append, don't replace

# State with message history (for chatbots)
class State(TypedDict):
    messages: Annotated[list, add_messages]     # Append + deduplicate
```

---

## 🏗️ Graph Building — Step by Step

```python
# 1. Create graph
graph = StateGraph(State)

# 2. Add nodes
graph.add_node("node_name", node_function)

# 3. Add edges
graph.add_edge(START, "first_node")       # Entry point
graph.add_edge("node_a", "node_b")        # Sequential
graph.add_edge("node_b", END)             # Exit point

# 4. Compile
app = graph.compile()                     # Without persistence
app = graph.compile(checkpointer=MemorySaver())  # With persistence

# 5. Run
result = app.invoke({"query": "Hello"})   # Full result
```

---

## 📊 All Edge Types

```python
# Sequential: A → B → C
graph.add_edge("A", "B")
graph.add_edge("B", "C")

# Parallel (fan-out): START → A, B, C simultaneously
graph.add_edge(START, "A")
graph.add_edge(START, "B")
graph.add_edge(START, "C")

# Aggregation (fan-in): A, B, C → D
graph.add_edge("A", "D")
graph.add_edge("B", "D")
graph.add_edge("C", "D")

# Conditional: A → (B or C) based on function
graph.add_conditional_edges("A", routing_function, {
    "option_1": "B",
    "option_2": "C"
})
```

---

## 🔀 Conditional Routing

```python
# Routing function: examines state, returns a string key
def route(state):
    if state["score"] > 70:
        return "pass"
    return "fail"

# Add to graph
graph.add_conditional_edges(
    "evaluator",          # Source node
    route,                # Routing function
    {                     # Key → node mapping
        "pass": "success_handler",
        "fail": "failure_handler"
    }
)
```

---

## 🔁 Loop Pattern

```python
def should_retry(state):
    if state["quality"] >= 80 or state["attempts"] >= 3:
        return "done"      # Exit loop
    return "retry"         # Loop back

graph.add_conditional_edges("evaluate", should_retry, {
    "retry": "generate",   # ← Loop back to previous node
    "done": END
})
```

---

## 💾 Persistence & Memory

```python
# Enable memory
app = graph.compile(checkpointer=MemorySaver())

# Use thread_id for isolated conversations
config = {"configurable": {"thread_id": "user_123"}}
result = app.invoke(input, config)

# Inspect state
state = app.get_state(config)               # Current state
history = app.get_state_history(config)      # All checkpoints

# Modify state manually
app.update_state(config, {"score": 95})

# Time travel — re-run from a past checkpoint
past = list(app.get_state_history(config))[2]
app.invoke(None, past.config)
```

---

## 📡 Streaming

```python
# Full state after each node
for state in app.stream(input, config, stream_mode="values"):
    print(state)

# Only deltas from each node
for update in app.stream(input, config, stream_mode="updates"):
    print(update)

# Token-by-token (for chat UIs)
for msg, metadata in app.stream(input, config, stream_mode="messages"):
    if hasattr(msg, "content") and msg.content:
        print(msg.content, end="")
```

---

## 🎯 Structured Output (Pydantic)

```python
from pydantic import BaseModel, Field

class Result(BaseModel):
    feedback: str = Field(description="Detailed feedback")
    score: int = Field(ge=0, le=100, description="Score 0-100")

structured_llm = llm.with_structured_output(Result)
result = structured_llm.invoke("Evaluate this essay...")

# Access with dot notation (NOT brackets!)
print(result.score)     # ✅ Correct
# print(result["score"]) # ❌ TypeError!
```

---

## 🤖 Prebuilt ReAct Agent

```python
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

@tool
def search(query: str) -> str:
    """Search the web."""
    return f"Results for {query}"

agent = create_react_agent(llm, tools=[search])
result = agent.invoke({"messages": [HumanMessage("Search for AI news")]})
```

---

## ⏸️ Human-in-the-Loop

```python
# Pause BEFORE a node
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["risky_action"]
)

# Run until pause
result = app.invoke(input, config)
# → Graph is paused before "risky_action"

# Human reviews, optionally edits state
app.update_state(config, {"approved": True})

# Resume
app.invoke(None, config)
```

---

## ⚠️ Common Mistakes & Fixes

| Mistake | Error | Fix |
|---------|-------|-----|
| Node returns raw value | `InvalidUpdateError` | Return `dict` always |
| Using `{}` for prompt messages | Scrambled message order | Use `[]` (list) |
| Bracket notation on Pydantic | `TypeError: not subscriptable` | Use dot notation |
| Wrong MemorySaver import | `ImportError` | `from langgraph.checkpoint.memory import MemorySaver` |
| No reducer for parallel state | Last writer wins | Use `Annotated[list, operator.add]` |
| Missing edge to END | Graph never terminates | `graph.add_edge("last", END)` |
| No `thread_id` with checkpointer | State not persisted | Pass `config = {"configurable": {"thread_id": "..."}}` |
| Loop without max retries | `GraphRecursionError` | Add `attempts` counter + exit condition |
| Missing `Field` import | `NameError` | `from pydantic import BaseModel, Field` |

---

## 📋 Node Function Template

```python
def my_node(state: MyState) -> dict:
    """
    Every node:
    1. Receives state as input
    2. Does some processing
    3. Returns a dict (partial state update)
    """
    # Your logic here
    result = process(state["input"])
    
    # Always return a dict!
    return {"output": result}
```

---

## 🗺️ Graph Pattern Templates

### Sequential
```
START → A → B → C → END
```

### Parallel (Fan-out / Fan-in)
```
START → A ──┐
START → B ──┼──→ Aggregator → END
START → C ──┘
```

### Conditional
```
Router → [condition_1] → Handler_1 → END
Router → [condition_2] → Handler_2 → END
```

### Iterative (Loop)
```
Generate → Evaluate → [retry] → Generate (loop)
                    → [done]  → END
```

### Chatbot
```
START → Chat → END  (with checkpointer + thread_id)
```

---

## 🔐 Environment Setup

```bash
# .env file
GROQ_API_KEY=gsk_your_key_here

# Install
pip install langgraph langchain langchain-groq python-dotenv pydantic

# Run
python your_script.py

# Streamlit
streamlit run app.py
```

---

## 📚 Key Terminology Quick Reference

| Term | Definition |
|------|-----------|
| **StateGraph** | Main class for building graphs |
| **Node** | A function performing a task |
| **Edge** | Connection between nodes |
| **State** | Shared data structure (TypedDict) |
| **Reducer** | Defines how parallel writes are merged |
| **Checkpointer** | Saves state after each node |
| **Thread ID** | Isolates conversations |
| **Compile** | Turns graph definition into runnable app |
| **Invoke** | Runs graph, returns full result |
| **Stream** | Runs graph, yields incremental results |
| **START / END** | Graph entry and exit sentinels |
| **Subgraph** | A graph nested inside another graph |
| **HITL** | Human-in-the-loop (pause for human input) |
| **Time Travel** | Go back to any previous checkpoint |
| **LangSmith** | Observability and tracing platform |

---

> ⬅️ [Back to Main Guide](./README.md) | ⬅️ [Previous: Scenario-Based Problems](./04_Scenario_Based.md)
>
> 🚀 **You're ready. Go ace that interview!**
