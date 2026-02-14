# 🧠 LangGraph — Learning Project

> A hands-on learning project for building **intelligent, stateful, multi-step LLM workflows** using [LangGraph](https://langchain-ai.github.io/langgraph/).

---

## 📖 Table of Contents

- [What is LangGraph?](#-what-is-langgraph)
- [Why LangGraph?](#-why-langgraph)
- [Key Definitions](#-key-definitions)
- [LLM Workflows](#-llm-workflows)
- [Graphs, Nodes & Edges](#-graphs-nodes--edges)
- [State](#-state)
- [Project Structure](#-project-structure)
- [What We Built](#-what-we-built)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [How to Run](#-how-to-run)
- [Example Graph Flow](#-example-graph-flow)
- [Common Errors & Fixes](#-common-errors--fixes)
- [Resources](#-resources)

---

## 🤔 What is LangGraph?

**LangGraph** is an orchestration framework for building intelligent, stateful, and multi-step LLM workflows. Instead of chaining prompts in a simple linear sequence, LangGraph lets you model your logic as a **graph of nodes (tasks) and edges (routing)**.

It enables advanced features like:
- ⚡ **Parallelism** — Run multiple tasks at the same time
- 🔁 **Loops** — Retry or iterate until a condition is met
- 🔀 **Branching** — Route to different nodes based on conditions
- 🧠 **Memory** — Persist state across conversations
- ⏸️ **Resumability** — Pause and resume workflows

This makes it ideal for **agentic** and **production-grade AI applications**.

---

## 💡 Why LangGraph?

| Feature | Simple Chain | LangGraph |
|---------|-------------|-----------|
| Linear execution | ✅ | ✅ |
| Parallel execution | ❌ | ✅ |
| Conditional routing | ❌ | ✅ |
| Loops & retries | ❌ | ✅ |
| State management | ❌ | ✅ |
| Conversation memory | ❌ | ✅ |
| Production-ready | ❌ | ✅ |

---

## 📚 Key Definitions

### 🔹 LLM (Large Language Model)
A Large Language Model is a type of AI model trained on massive amounts of text data. It can understand and generate human-like text. Examples: GPT-4, Llama 3, Gemini, Claude.

### 🔹 LangChain
LangChain is a Python framework for building applications powered by LLMs. It provides tools for prompts, chains, memory, tools, and agents. LangGraph is built on top of LangChain.

### 🔹 Groq
Groq is an AI inference company that provides ultra-fast LLM API access. We use their API to run the `llama-3.3-70b-versatile` model in this project.

### 🔹 Pydantic
Pydantic is a data validation library for Python. We use Pydantic `BaseModel` to define structured output schemas — forcing the LLM to return data in a specific format (e.g., `feedback: str`, `score: int`).

### 🔹 StateGraph
The main class in LangGraph. You define your state type, add nodes (functions), connect them with edges, and compile the graph into a runnable application.

### 🔹 Checkpointer (MemorySaver)
A checkpointer saves the state of the graph after each node execution. `MemorySaver` is an in-memory checkpointer — it enables conversation memory (multi-turn chat) by persisting state between invocations.

---

## 🔄 LLM Workflows

LLM workflows are a step-by-step process using which we can build complex LLM applications or a series of tasks to achieve a goal.

Each step in a workflow performs a distinct task — such as prompting, reasoning, tool calling, memory access, or decision-making.

Workflows can be **linear**, **parallel**, **branched**, or **looped**.

### Common Workflow Patterns

#### 1. 🔗 Prompt Chaining
- **What**: Breaking a complex task into a sequence of simpler prompts where each prompt uses the previous prompt's output as input.
- **How**: Solve one subtask at a time → pass its result to the next prompt → compose final output from intermediate results.
- **Why**: Improves reliability, control, and traceability for complex requests.
- **Example in this project**: `Sequential Workflow 2.py` — Generate outline → Write draft → Polish & summarize.

#### 2. 🚦 Routing
- **What**: Direct each incoming task/request to the correct handler or service based on rules, metadata, or content.
- **How**: Incoming message → identify intent → route to the right handler → return response.
- **Why**: Different types of inputs often need different processing logic.

#### 3. ⚡ Parallelization
- **What**: Run multiple independent LLM calls or tasks **at the same time** to reduce latency and increase throughput.
- **How**: For a given task, break it into multiple subtasks, execute all subtasks concurrently, and then merge their results.
- **Why**: When tasks are independent of each other, running them in parallel is significantly faster.
- **Example in this project**: `Parallel Workflow 2.py` — Evaluate language, analysis, and clarity simultaneously.

#### 4. 🎯 Orchestrator Workers
- **What**: Components that schedule, execute, and monitor workflow nodes, coordinating concurrent runs, retries, and state transitions.
- **How**: Orchestrator dispatches workers → each worker runs a task → reports results back → orchestrator merges and advances.
- **Why**: Enables scalable, fault-tolerant workflow execution.

#### 5. 📊 Evaluator Optimizer
- **What**: A component that scores, ranks, and selects candidate outputs to produce the best final result.
- **How**: Generate multiple candidate responses → score each using metrics → choose or ensemble the best.
- **Why**: Improves output quality by selecting from multiple attempts.

---

## 🏗️ Graphs, Nodes & Edges

### 1. Graph
A **Graph** is the overarching structure that maps out how different tasks (nodes) are connected and executed. It visually represents the workflow, showing the sequence and conditional paths between various operations.

> 🗺️ **Analogy**: A road map displaying different routes connecting cities, with intersections offering choices on which path to take next.

### 2. Node
**Nodes** are individual functions or operations that perform specific tasks within the graph. Each node receives input (the current state), processes it, and produces an output (updated state).

> 🏭 **Analogy**: Assembly line stations — each station does one job: attach a part, paint it, inspect quality, and so on.

**Important Rules:**
- Every node function receives the current state as input.
- Every node function **must return a `dict`** (partial state update) — never return raw values like `float` or `str`.
- Nodes can contain any Python logic — LLM calls, computations, API calls, etc.

### 3. Edges
**Edges** are the connections between nodes that determine the flow of execution. They tell us which node should be executed next after the current one completes.

> 🛤️ **Analogy**: Train tracks connecting stations together in a specific direction.

**Types of Edges:**
```python
# Normal edge — A always goes to B
graph.add_edge('node_a', 'node_b')

# Fan-out — START goes to multiple nodes (parallel execution)
graph.add_edge(START, 'node_a')
graph.add_edge(START, 'node_b')
graph.add_edge(START, 'node_c')

# Fan-in — Multiple nodes go to one aggregator
graph.add_edge('node_a', 'aggregator')
graph.add_edge('node_b', 'aggregator')
graph.add_edge('node_c', 'aggregator')
```

---

## 📦 State

The **State** is a shared data structure that holds the current information or context of the entire application. In simple terms, it is the application's memory — keeping track of variables and data that nodes can access and modify as they execute.

> 📋 **Analogy**: A whiteboard in a meeting room — participants (nodes) write and read information on the whiteboard (state) to stay updated and coordinate actions.

### Defining State

State is typically defined using Python's `TypedDict`:

```python
from typing import TypedDict

class MyState(TypedDict):
    query: str
    response: str
    score: float
```

### State Reducers (for Parallel Workflows)

When multiple parallel nodes write to the same state key, you need a **reducer** to define how to combine the values:

```python
from typing import Annotated, List
import operator

class MyState(TypedDict):
    # operator.add means: APPEND to the list instead of replacing
    scores: Annotated[List[int], operator.add]
```

Without a reducer, the last node to finish would overwrite the value from previous nodes.

---

## 📂 Project Structure

```
LangGraph/
├── 📄 README.md                    ← You are here
├── 📄 requirements.txt             ← Python dependencies
├── 📄 .env                         ← Environment variables (GROQ_API_KEY)
├── 📄 .gitignore                   ← Git ignore rules
│
├── 📁 Basic Bot/
│   ├── 📄 ChatBot.py               ← Interactive chatbot with memory
│   └── 📄 README.md                ← Docs for this section
│
├── 📁 Sequential Workflow/
│   ├── 📄 Sequential Workflow 1.py ← Simple single-node LLM query
│   ├── 📄 Sequential Workflow.py   ← BMI Calculator (2 nodes)
│   ├── 📄 Sequential Workflow 2.py ← Blog Post Generator (prompt chaining, 3 nodes)
│   └── 📄 README.md                ← Docs for this section
│
├── 📁 Parallel Workflow/
│   ├── 📄 Parallel Workflow.py     ← Cricket Player Stats (3 parallel nodes)
│   ├── 📄 Parallel Workflow 1.py   ← Structured LLM Output with Pydantic
│   ├── 📄 Parallel Workflow 2.py   ← UPSE Essay Evaluator (parallel LLM evaluation)
│   └── 📄 README.md                ← Docs for this section
│
└── 📁 langvenv/                    ← Python virtual environment
```

---

## 🏆 What We Built

### Module 1: Basic Bot — [`Basic Bot/`](./Basic%20Bot/)
An interactive **chatbot with conversation memory**. Uses `MemorySaver` checkpointer to remember previous messages across turns. Runs in a loop — type messages and get AI responses.

### Module 2: Sequential Workflow — [`Sequential Workflow/`](./Sequential%20Workflow/)
Three examples of **sequential (linear) workflows** where nodes execute one after another:
1. **Simple LLM Query** — Single node that sends a query to the LLM.
2. **BMI Calculator** — Two nodes: calculate BMI → label the category. Pure computation, no LLM.
3. **Blog Post Generator** — Three-step **prompt chaining**: generate outline → write draft → polish & summarize.

### Module 3: Parallel Workflow — [`Parallel Workflow/`](./Parallel%20Workflow/)
Three examples of **parallel execution** where multiple nodes run simultaneously:
1. **Cricket Player Stats** — Three stats computed in parallel, then summarized.
2. **Structured LLM Output** — Using Pydantic `BaseModel` to force the LLM to return typed data.
3. **UPSE Essay Evaluator** — Three LLM evaluators run in parallel (language, analysis, clarity), then an aggregator produces the overall score.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| [Python 3.10+](https://www.python.org/) | Programming language |
| [LangGraph](https://langchain-ai.github.io/langgraph/) | Graph-based workflow orchestration |
| [LangChain](https://www.langchain.com/) | LLM framework (core, messages, tools) |
| [LangChain-Groq](https://python.langchain.com/docs/integrations/chat/groq/) | Groq LLM integration for LangChain |
| [Groq API](https://console.groq.com/) | Ultra-fast LLM inference (Llama 3.3 70B) |
| [Pydantic](https://docs.pydantic.dev/) | Data validation & structured output |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Load environment variables from `.env` file |

---

## ✅ Prerequisites

Before you begin, make sure you have:

1. **Python 3.10 or higher** installed on your machine.
   ```bash
   python --version
   ```

2. **A Groq API Key** — Sign up for free at [console.groq.com](https://console.groq.com/) and create an API key.

3. **Git** (optional) — For cloning and version control.

---

## 🚀 Installation & Setup

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd LangGraph
```

### Step 2: Create a Virtual Environment

```bash
python -m venv langvenv
```

### Step 3: Activate the Virtual Environment

**Windows (PowerShell):**
```powershell
.\langvenv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.\langvenv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
source langvenv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `langchain` — Core LangChain framework
- `langchain-core` — Core abstractions (messages, prompts)
- `langchain-community` — Community integrations
- `langchain-groq` — Groq LLM integration
- `python-dotenv` — Environment variable management
- `langgraph` — Graph-based workflow orchestration
- `pydantic` — Data validation for structured output

### Step 5: Configure Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> ⚠️ **Never commit your `.env` file to Git.** Make sure it's listed in `.gitignore`.

---

## ▶️ How to Run

### 1. Activate the Virtual Environment

```powershell
.\langvenv\Scripts\Activate.ps1
```

### 2. Run Any Script

```bash
# Basic Bot — Interactive chatbot
python "Basic Bot/ChatBot.py"

# Sequential Workflow — Simple LLM query
python "Sequential Workflow/Sequential Workflow 1.py"

# Sequential Workflow — BMI Calculator
python "Sequential Workflow/Sequential Workflow.py"

# Sequential Workflow — Blog Post Generator (Prompt Chaining)
python "Sequential Workflow/Sequential Workflow 2.py"

# Parallel Workflow — Cricket Player Stats
python "Parallel Workflow/Parallel Workflow.py"

# Parallel Workflow — Structured LLM Output
python "Parallel Workflow/Parallel Workflow 1.py"

# Parallel Workflow — UPSE Essay Evaluator
python "Parallel Workflow/Parallel Workflow 2.py"
```

---

## 🗺️ Example Graph Flow

### UPSC Essay Evaluation System (What We Are Building Towards)

The system generates an essay topic, collects the student's submission, and evaluates it in parallel on depth of analysis, language quality, and clarity of thought. Based on the combined score, it either gives feedback for improvement or approves the essay.

```
┌─────────────────┐
│  GenerateTopic  │
└────────┬────────┘
         ▼
┌─────────────────┐
│  CollectEssay   │
└────────┬────────┘
         ▼
┌─────────────────────────────────────────────┐
│         EvaluateEssay (Parallel)            │
│                                             │
│  ┌──────────────┐  ┌───────────────────┐    │
│  │EvaluateDepth │  │ EvaluateLanguage  │    │
│  └──────────────┘  └───────────────────┘    │
│          ┌──────────────────┐               │
│          │ EvaluateClarity  │               │
│          └──────────────────┘               │
└────────────────────┬────────────────────────┘
                     ▼
          ┌──────────────────┐
          │ AggregateResults │
          └────────┬─────────┘
                   ▼
          ┌──────────────────┐
          │ConditionalRouting│
          └───┬──────────┬───┘
              ▼          ▼
     ┌────────────┐  ┌──────────────┐
     │GiveFeedback│  │ ShowSuccess  │
     └──────┬─────┘  └──────────────┘
            │
            ▼
     ┌────────────────┐
     │CollectRevision │ ──→ (Loop back to EvaluateEssay)
     └────────────────┘
```

#### Steps:
1. **GenerateTopic** — System generates a relevant UPSC-style essay topic.
2. **CollectEssay** — Student writes and submits the essay.
3. **EvaluateEssay** (Parallel) — Three evaluations run simultaneously:
   - **EvaluateDepth** — Analyzes depth of analysis, argument strength, critical thinking.
   - **EvaluateLanguage** — Checks grammar, vocabulary, fluency, and tone.
   - **EvaluateClarity** — Assesses coherence, logical flow, and clarity of thought.
4. **AggregateResults** — Combines scores and generates a total score.
5. **ConditionalRouting** — Routes based on score:
   - Score meets threshold → **ShowSuccess** ✅
   - Score below threshold → **GiveFeedback** ❌
6. **GiveFeedback** — Provides targeted suggestions for improvement.
7. **CollectRevision** (optional loop) — Student resubmits → loop back to evaluation.
8. **ShowSuccess** — Congratulates the student and ends the flow.

---

## ⚠️ Common Errors & Fixes

Here are the errors we encountered and fixed while building this project:

### 1. `ModuleNotFoundError: No module named 'langgraph'`
**Cause:** Dependencies not installed in the virtual environment.
**Fix:**
```bash
pip install -r requirements.txt
```

### 2. `InvalidUpdateError: Expected dict, got 2.0`
**Cause:** Node functions returning raw values (`float`, `str`) instead of dictionaries.
**Fix:** Always return a `dict` from node functions:
```python
# ❌ Wrong
def my_node(state):
    return 42

# ✅ Correct
def my_node(state):
    return {'score': 42}
```

### 3. `TypeError: 'ResponseState' object is not subscriptable`
**Cause:** Using bracket notation on a Pydantic object.
**Fix:** Use dot notation for Pydantic objects:
```python
# ❌ Wrong
response['feedback']

# ✅ Correct
response.feedback
```

### 4. `ImportError: cannot import name 'MemorySaver' from 'langgraph.graph.memory'`
**Cause:** Import path changed in newer versions of LangGraph.
**Fix:**
```python
# ❌ Old path
from langgraph.graph.memory import MemorySaver

# ✅ New path
from langgraph.checkpoint.memory import MemorySaver
```

### 5. Using `{}` (set) instead of `[]` (list) for prompt messages
**Cause:** Sets are unordered and not valid input for LLM invocation.
**Fix:**
```python
# ❌ Wrong — this creates a set (unordered!)
prompt = {
    SystemMessage(content="..."),
    HumanMessage(content="...")
}

# ✅ Correct — this creates a list (ordered)
prompt = [
    SystemMessage(content="..."),
    HumanMessage(content="...")
]
```

### 6. `NameError: name 'Field' is not defined`
**Cause:** Using `Field()` without importing it from Pydantic.
**Fix:**
```python
from pydantic import BaseModel, Field
```

---

## 📚 Resources

- 📘 [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- 📘 [LangChain Documentation](https://python.langchain.com/docs/)
- 📘 [Groq Console](https://console.groq.com/)
- 📘 [Pydantic Documentation](https://docs.pydantic.dev/)
- 📘 [LangGraph GitHub](https://github.com/langchain-ai/langgraph)

---

## 📝 License

This is a personal learning project. Feel free to use it for your own learning!

---

> Built with ❤️ using LangGraph + Groq + LangChain