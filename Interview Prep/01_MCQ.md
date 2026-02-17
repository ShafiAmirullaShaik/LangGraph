# 📝 LangGraph — Multiple Choice Questions

> Test your conceptual understanding across all levels.
> **Answers are hidden in expandable sections** — try answering before peeking!

---

## 📌 How to Use
1. Read each question carefully
2. Pick your answer **before** expanding the solution
3. Check the explanation to understand the *why*
4. Track your score: aim for **90%+** before your interview

---

## ⭐ Section 1: Basic (Questions 1–20)

### Q1. What is LangGraph primarily used for?
- A) Training large language models
- B) Building stateful, multi-step LLM workflows as graphs
- C) Fine-tuning transformer models
- D) Creating vector databases

<details>
<summary>✅ Answer</summary>

**B) Building stateful, multi-step LLM workflows as graphs**

LangGraph is an orchestration framework that models LLM application logic as a graph of nodes (tasks) and edges (routing). It does not train or fine-tune models.
</details>

---

### Q2. Which data structure does LangGraph use to represent workflows?
- A) Linked List
- B) Binary Tree
- C) Directed Graph
- D) Hash Map

<details>
<summary>✅ Answer</summary>

**C) Directed Graph**

LangGraph uses a directed graph where nodes represent functions/operations and edges represent the flow of execution between them.
</details>

---

### Q3. What is a "Node" in LangGraph?
- A) A database connection
- B) A function or operation that performs a specific task
- C) A type of LLM model
- D) A configuration file

<details>
<summary>✅ Answer</summary>

**B) A function or operation that performs a specific task**

Nodes are individual functions that receive the current state, process it, and return an updated state (as a dictionary).
</details>

---

### Q4. What must every node function return in LangGraph?
- A) A string
- B) A list
- C) A dictionary (dict)
- D) A tuple

<details>
<summary>✅ Answer</summary>

**C) A dictionary (dict)**

Every node function must return a `dict` representing a partial state update. Returning raw values like `float` or `str` will cause an `InvalidUpdateError`.
</details>

---

### Q5. What are `START` and `END` in LangGraph?
- A) Python functions
- B) Special sentinel nodes marking the beginning and end of a graph
- C) Names of LLM models
- D) Types of edges

<details>
<summary>✅ Answer</summary>

**B) Special sentinel nodes marking the beginning and end of a graph**

`START` marks the entry point of the graph and `END` marks the termination point. They are imported from `langgraph.graph`.
</details>

---

### Q6. Which class is used to create a graph in LangGraph?
- A) `GraphBuilder`
- B) `StateGraph`
- C) `WorkflowGraph`
- D) `DAGBuilder`

<details>
<summary>✅ Answer</summary>

**B) StateGraph**

`StateGraph` is the main class. You define a state type, add nodes and edges, and then compile it into a runnable application.

```python
from langgraph.graph import StateGraph
graph = StateGraph(MyState)
```
</details>

---

### Q7. How do you define the state schema in LangGraph?
- A) Using a JSON file
- B) Using Python's `TypedDict`
- C) Using XML configuration
- D) Using environment variables

<details>
<summary>✅ Answer</summary>

**B) Using Python's `TypedDict`**

```python
from typing import TypedDict

class MyState(TypedDict):
    query: str
    response: str
```
</details>

---

### Q8. What happens after you define nodes and edges in a `StateGraph`?
- A) It auto-executes
- B) You must call `.compile()` to create a runnable application
- C) You save it to a file
- D) You deploy it to a server

<details>
<summary>✅ Answer</summary>

**B) You must call `.compile()` to create a runnable application**

```python
app = graph.compile()
result = app.invoke(initial_state)
```
</details>

---

### Q9. What is the relationship between LangGraph and LangChain?
- A) They are completely unrelated
- B) LangGraph is built on top of LangChain
- C) LangChain is built on top of LangGraph
- D) They are the same library

<details>
<summary>✅ Answer</summary>

**B) LangGraph is built on top of LangChain**

LangGraph extends LangChain by adding graph-based workflow orchestration with features like loops, branching, state management, and persistence that simple LangChain chains don't support.
</details>

---

### Q10. Which of the following is NOT a workflow pattern supported by LangGraph?
- A) Sequential
- B) Parallel
- C) Recursive Neural
- D) Conditional

<details>
<summary>✅ Answer</summary>

**C) Recursive Neural**

LangGraph supports Sequential, Parallel, Conditional, and Iterative (loop) patterns. "Recursive Neural" is not a LangGraph workflow pattern — it's a neural network architecture concept.
</details>

---

### Q11. How do you add a node to a `StateGraph`?
- A) `graph.create_node("name", function)`
- B) `graph.add_node("name", function)`
- C) `graph.register("name", function)`
- D) `graph.node("name", function)`

<details>
<summary>✅ Answer</summary>

**B) `graph.add_node("name", function)`**

```python
graph.add_node("process", my_function)
```
</details>

---

### Q12. How do you connect two nodes with a direct edge?
- A) `graph.connect("node_a", "node_b")`
- B) `graph.add_edge("node_a", "node_b")`
- C) `graph.link("node_a", "node_b")`
- D) `graph.pipe("node_a", "node_b")`

<details>
<summary>✅ Answer</summary>

**B) `graph.add_edge("node_a", "node_b")`**

```python
graph.add_edge("node_a", "node_b")
```
</details>

---

### Q13. What is the correct import path for `MemorySaver` in current LangGraph versions?
- A) `from langgraph.graph.memory import MemorySaver`
- B) `from langgraph.checkpoint.memory import MemorySaver`
- C) `from langchain.memory import MemorySaver`
- D) `from langgraph.memory import MemorySaver`

<details>
<summary>✅ Answer</summary>

**B) `from langgraph.checkpoint.memory import MemorySaver`**

The import path changed in newer versions. The old path `langgraph.graph.memory` no longer works.
</details>

---

### Q14. What does `.invoke()` do on a compiled graph?
- A) Compiles the graph
- B) Adds a new node
- C) Runs the graph with given input and returns the final state
- D) Saves the graph to disk

<details>
<summary>✅ Answer</summary>

**C) Runs the graph with given input and returns the final state**

```python
result = app.invoke({"query": "Hello"})
```
</details>

---

### Q15. In a sequential workflow, how do nodes execute?
- A) All at once in parallel
- B) Randomly
- C) One after another, in order
- D) Only if a condition is met

<details>
<summary>✅ Answer</summary>

**C) One after another, in order**

In a sequential workflow, each node completes before the next one begins: A → B → C.
</details>

---

### Q16. What is "prompt chaining" in LangGraph?
- A) Connecting multiple LLMs together
- B) Breaking a complex task into a sequence of simpler prompts where each uses the previous output
- C) Encrypting prompts for security
- D) Caching prompts for reuse

<details>
<summary>✅ Answer</summary>

**B) Breaking a complex task into a sequence of simpler prompts where each uses the previous output**

Example: Generate outline → Write draft → Polish & summarize. Each step uses the output of the previous step.
</details>

---

### Q17. Which message types are commonly used with LangChain LLMs?
- A) `TextMessage` and `DataMessage`
- B) `SystemMessage`, `HumanMessage`, and `AIMessage`
- C) `InputMessage` and `OutputMessage`
- D) `RequestMessage` and `ResponseMessage`

<details>
<summary>✅ Answer</summary>

**B) `SystemMessage`, `HumanMessage`, and `AIMessage`**

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
```
</details>

---

### Q18. What error occurs if a node function returns a raw value like `42` instead of a `dict`?
- A) `TypeError`
- B) `ValueError`
- C) `InvalidUpdateError`
- D) `NodeReturnError`

<details>
<summary>✅ Answer</summary>

**C) `InvalidUpdateError`**

LangGraph expects all node functions to return a dictionary for partial state updates. Returning raw values triggers `InvalidUpdateError: Expected dict, got <value>`.
</details>

---

### Q19. What does `.add_edge(START, "node_a")` do?
- A) Creates a conditional edge
- B) Sets `node_a` as the first node to execute when the graph starts
- C) Creates a loop back to the beginning
- D) Deletes the node

<details>
<summary>✅ Answer</summary>

**B) Sets `node_a` as the first node to execute when the graph starts**

`START` is a sentinel that represents the graph entry point. Connecting it to a node makes that node the first to execute.
</details>

---

### Q20. What does `.add_edge("node_a", END)` do?
- A) Loops back to node_a
- B) Pauses execution
- C) Marks node_a's output as the final state and terminates the graph
- D) Adds a new node called END

<details>
<summary>✅ Answer</summary>

**C) Marks node_a's output as the final state and terminates the graph**

`END` is a sentinel that signals the graph execution is complete after the connected node finishes.
</details>

---

## ⭐⭐ Section 2: Intermediate (Questions 21–40)

### Q21. What is the purpose of a "state reducer" in LangGraph?
- A) To reduce the size of the state object
- B) To define how values from multiple parallel nodes are combined into a single state key
- C) To compress state for network transfer
- D) To delete old state values

<details>
<summary>✅ Answer</summary>

**B) To define how values from multiple parallel nodes are combined into a single state key**

Without a reducer, the last node to finish would overwrite values from previous nodes. Reducers like `operator.add` append instead of replacing.

```python
from typing import Annotated
import operator

class MyState(TypedDict):
    scores: Annotated[list[int], operator.add]
```
</details>

---

### Q22. How do you create a parallel workflow in LangGraph (fan-out)?
- A) Use a `for` loop inside a node
- B) Connect `START` (or a single node) to multiple nodes with separate edges
- C) Use Python's `asyncio` module
- D) Call `.invoke()` multiple times

<details>
<summary>✅ Answer</summary>

**B) Connect `START` (or a single node) to multiple nodes with separate edges**

```python
graph.add_edge(START, "eval_language")
graph.add_edge(START, "eval_clarity")
graph.add_edge(START, "eval_depth")
```
All three nodes will run simultaneously.
</details>

---

### Q23. What is "fan-in" in a parallel workflow?
- A) Splitting one task into many
- B) Multiple parallel nodes converging into a single aggregator node
- C) Broadcasting the same input to all nodes
- D) Reducing the number of nodes

<details>
<summary>✅ Answer</summary>

**B) Multiple parallel nodes converging into a single aggregator node**

```python
graph.add_edge("eval_language", "aggregator")
graph.add_edge("eval_clarity", "aggregator")
graph.add_edge("eval_depth", "aggregator")
```
</details>

---

### Q24. What method is used to add conditional routing in LangGraph?
- A) `graph.add_edge()`
- B) `graph.add_conditional_edges()`
- C) `graph.add_router()`
- D) `graph.add_switch()`

<details>
<summary>✅ Answer</summary>

**B) `graph.add_conditional_edges()`**

```python
graph.add_conditional_edges(
    "router_node",
    routing_function,
    {"positive": "handle_positive", "negative": "handle_negative"}
)
```
</details>

---

### Q25. What must the routing function in `add_conditional_edges()` return?
- A) A boolean (`True` / `False`)
- B) A string matching one of the mapped keys
- C) A node function
- D) An integer

<details>
<summary>✅ Answer</summary>

**B) A string matching one of the mapped keys**

The routing function examines the current state and returns a string key that maps to the next node in the conditional edge mapping.

```python
def route(state):
    if state["score"] > 70:
        return "pass"
    return "fail"
```
</details>

---

### Q26. What is a `Checkpointer` in LangGraph?
- A) A testing tool
- B) A component that saves graph state after each node execution
- C) A code linter
- D) A performance profiler

<details>
<summary>✅ Answer</summary>

**B) A component that saves graph state after each node execution**

Checkpointers enable persistence, conversation memory, fault tolerance, and time travel by saving state snapshots after each node.
</details>

---

### Q27. What is `MemorySaver` in LangGraph?
- A) A disk-based database
- B) An in-memory checkpointer for development and testing
- C) A GPU memory manager
- D) A prompt caching system

<details>
<summary>✅ Answer</summary>

**B) An in-memory checkpointer for development and testing**

`MemorySaver` stores checkpoints in RAM. It's great for development but data is lost when the process restarts. For production, use database-backed checkpointers.
</details>

---

### Q28. How do you enable memory/persistence when compiling a graph?
- A) `graph.compile(memory=True)`
- B) `graph.compile(checkpointer=MemorySaver())`
- C) `graph.compile(persist=True)`
- D) `graph.compile(save_state=True)`

<details>
<summary>✅ Answer</summary>

**B) `graph.compile(checkpointer=MemorySaver())`**

```python
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()
app = graph.compile(checkpointer=memory)
```
</details>

---

### Q29. What is the `thread_id` used for in LangGraph?
- A) Managing Python threads
- B) Identifying separate conversation threads so state is isolated per thread
- C) Debugging thread-safety issues
- D) Logging purposes

<details>
<summary>✅ Answer</summary>

**B) Identifying separate conversation threads so state is isolated per thread**

```python
config = {"configurable": {"thread_id": "user_123"}}
result = app.invoke({"messages": [msg]}, config=config)
```
Each `thread_id` maintains its own conversation history and state.
</details>

---

### Q30. What does the `add_messages` reducer do?
- A) Adds new messages to a database
- B) Appends new messages to the existing message list instead of replacing it
- C) Sends messages to an API
- D) Formats messages for display

<details>
<summary>✅ Answer</summary>

**B) Appends new messages to the existing message list instead of replacing it**

```python
from langgraph.graph import add_messages
from typing import Annotated

class State(TypedDict):
    messages: Annotated[list, add_messages]
```
Without this reducer, each node would overwrite the message history instead of appending to it.
</details>

---

### Q31. Which of the following correctly uses Pydantic for structured LLM output?
- A) `llm.invoke(prompt, format="json")`
- B) `llm.with_structured_output(MyPydanticModel)`
- C) `llm.invoke(prompt).to_pydantic()`
- D) `json.loads(llm.invoke(prompt))`

<details>
<summary>✅ Answer</summary>

**B) `llm.with_structured_output(MyPydanticModel)`**

```python
from pydantic import BaseModel

class Response(BaseModel):
    feedback: str
    score: int

structured_llm = llm.with_structured_output(Response)
result = structured_llm.invoke(prompt)  # Returns a Response object
```
</details>

---

### Q32. When using Pydantic structured output, how do you access fields?
- A) `response["feedback"]` (bracket notation)
- B) `response.feedback` (dot notation)
- C) `response.get("feedback")`
- D) `response->feedback`

<details>
<summary>✅ Answer</summary>

**B) `response.feedback` (dot notation)**

Pydantic objects use attribute access (dot notation). Using bracket notation (`response["feedback"]`) causes a `TypeError: object is not subscriptable`.
</details>

---

### Q33. What is streaming in LangGraph?
- A) Saving data to a stream file
- B) Receiving output token-by-token in real-time instead of waiting for the full response
- C) Compressing data for transfer
- D) Broadcasting to multiple users

<details>
<summary>✅ Answer</summary>

**B) Receiving output token-by-token in real-time instead of waiting for the full response**

```python
for chunk in app.stream(input, config, stream_mode="messages"):
    print(chunk)  # Prints tokens as they arrive
```
</details>

---

### Q34. What are the common `stream_mode` options in LangGraph?
- A) `"text"` and `"binary"`
- B) `"values"`, `"updates"`, and `"messages"`
- C) `"fast"` and `"slow"`
- D) `"sync"` and `"async"`

<details>
<summary>✅ Answer</summary>

**B) `"values"`, `"updates"`, and `"messages"`**

- `"values"` — Emits the full state after each node
- `"updates"` — Emits only the state changes from each node
- `"messages"` — Emits LLM tokens as they're generated (for chat UIs)
</details>

---

### Q35. What is the purpose of `get_state()` in LangGraph?
- A) Returns the graph definition
- B) Returns the current state snapshot for a given thread
- C) Returns the Python interpreter state
- D) Returns available memory

<details>
<summary>✅ Answer</summary>

**B) Returns the current state snapshot for a given thread**

```python
state = app.get_state(config)
print(state.values)  # Current state values
```
</details>

---

### Q36. What does `get_state_history()` return?
- A) All states from all threads
- B) A list of all checkpoint snapshots for a given thread, in reverse chronological order
- C) The history of graph definitions
- D) Log files

<details>
<summary>✅ Answer</summary>

**B) A list of all checkpoint snapshots for a given thread, in reverse chronological order**

```python
for state in app.get_state_history(config):
    print(state.values, state.metadata)
```
This enables time-travel debugging.
</details>

---

### Q37. What is "time travel" in LangGraph?
- A) Scheduling future executions
- B) Going back to a previous checkpoint and re-running the graph from that point
- C) Predicting future states
- D) Timezone management

<details>
<summary>✅ Answer</summary>

**B) Going back to a previous checkpoint and re-running the graph from that point**

You can retrieve a past checkpoint from `get_state_history()`, use its `config` as the starting point, and re-invoke the graph from that historical state.
</details>

---

### Q38. What does `update_state()` allow you to do?
- A) Update the graph structure at runtime
- B) Manually modify the state at a specific checkpoint
- C) Update Python packages
- D) Update the LLM model

<details>
<summary>✅ Answer</summary>

**B) Manually modify the state at a specific checkpoint**

```python
app.update_state(config, {"score": 95})
```
This is useful for human-in-the-loop workflows where you need to inject manual changes.
</details>

---

### Q39. Why should you use `[]` (list) instead of `{}` (set) for LLM prompt messages?
- A) Lists are faster
- B) Sets are unordered, which scrambles message order; lists preserve order
- C) Sets don't support strings
- D) LLMs only accept lists

<details>
<summary>✅ Answer</summary>

**B) Sets are unordered, which scrambles message order; lists preserve order**

```python
# ❌ Wrong — set (unordered)
prompt = {SystemMessage(content="..."), HumanMessage(content="...")}

# ✅ Correct — list (ordered)
prompt = [SystemMessage(content="..."), HumanMessage(content="...")]
```
</details>

---

### Q40. What is the role of `.env` and `python-dotenv` in a LangGraph project?
- A) They define the graph structure
- B) They securely store API keys and load them as environment variables
- C) They configure the Python runtime
- D) They manage virtual environments

<details>
<summary>✅ Answer</summary>

**B) They securely store API keys and load them as environment variables**

```python
from dotenv import load_dotenv
load_dotenv()  # Loads GROQ_API_KEY from .env file
```
This avoids hardcoding secrets in source code.
</details>

---

## ⭐⭐⭐ Section 3: Advanced (Questions 41–55)

### Q41. What is a "subgraph" in LangGraph?
- A) A smaller version of the graph with fewer nodes
- B) A graph nested inside another graph as a single node
- C) A graph that runs on a separate server
- D) A graph with only conditional edges

<details>
<summary>✅ Answer</summary>

**B) A graph nested inside another graph as a single node**

Subgraphs allow you to compose complex workflows by encapsulating a complete graph as a node in a parent graph. This promotes modularity and reusability.
</details>

---

### Q42. What is "human-in-the-loop" in LangGraph?
- A) A training technique
- B) Pausing graph execution to get human approval or input before continuing
- C) Using a GUI
- D) Manual testing

<details>
<summary>✅ Answer</summary>

**B) Pausing graph execution to get human approval or input before continuing**

LangGraph supports `interrupt_before` and `interrupt_after` to pause at specific nodes, wait for human input, and resume execution. This is critical for workflows that need human oversight.

```python
app = graph.compile(
    checkpointer=memory,
    interrupt_before=["sensitive_action"]
)
```
</details>

---

### Q43. What happens if two parallel nodes write to the same state key WITHOUT a reducer?
- A) Both values are saved in a list
- B) An error is thrown
- C) The last node to finish overwrites the other's value (race condition)
- D) The first node's value is kept

<details>
<summary>✅ Answer</summary>

**C) The last node to finish overwrites the other's value (race condition)**

Without a reducer, whichever node finishes last sets the final value for that state key. This is why reducers are essential for parallel workflows.
</details>

---

### Q44. How does LangGraph handle fault tolerance with checkpointers?
- A) It retries the entire graph from the beginning
- B) It resumes execution from the last successful checkpoint
- C) It ignores the error and continues
- D) It sends an alert email

<details>
<summary>✅ Answer</summary>

**B) It resumes execution from the last successful checkpoint**

If a crash occurs mid-execution, LangGraph can reload the last saved checkpoint and re-run only the remaining nodes. No work is lost from previously completed nodes.
</details>

---

### Q45. What is the difference between `MemorySaver` and a database-backed checkpointer?
- A) No difference
- B) `MemorySaver` stores in RAM (lost on restart); database-backed persists across restarts
- C) `MemorySaver` is faster but less accurate
- D) Database-backed only works with SQL databases

<details>
<summary>✅ Answer</summary>

**B) `MemorySaver` stores in RAM (lost on restart); database-backed persists across restarts**

`MemorySaver` is for development. In production, use `SqliteSaver`, `PostgresSaver`, or other database-backed checkpointers for durable persistence.
</details>

---

### Q46. What is the difference between `app.invoke()` and `app.stream()`?
- A) `invoke()` is synchronous, `stream()` is asynchronous
- B) `invoke()` waits for the full result; `stream()` yields results incrementally as they're produced
- C) `invoke()` runs one node, `stream()` runs all nodes
- D) They are identical

<details>
<summary>✅ Answer</summary>

**B) `invoke()` waits for the full result; `stream()` yields results incrementally as they're produced**

Use `invoke()` when you need the complete output. Use `stream()` for real-time UIs where you want to show progress (e.g., token-by-token streaming in a chatbot).
</details>

---

### Q47. How would you implement a retry loop in LangGraph?
- A) Use a Python `while` loop inside a node
- B) Use a conditional edge that routes back to a previous node when quality is insufficient
- C) Call `.invoke()` multiple times
- D) Use `try/except` blocks

<details>
<summary>✅ Answer</summary>

**B) Use a conditional edge that routes back to a previous node when quality is insufficient**

```python
graph.add_conditional_edges(
    "evaluate",
    check_quality,
    {"retry": "generate", "done": END}
)
```
This creates a loop: generate → evaluate → (retry → generate) until the output meets quality criteria.
</details>

---

### Q48. What are "tool nodes" in LangGraph?
- A) Nodes that build physical tools
- B) Nodes that execute external tools/functions called by the LLM (e.g., web search, calculator)
- C) Debugging utilities
- D) Configuration nodes

<details>
<summary>✅ Answer</summary>

**B) Nodes that execute external tools/functions called by the LLM (e.g., web search, calculator)**

LangGraph supports tool-calling agents where the LLM decides which tools to invoke, and tool nodes execute those functions and return results to the LLM.
</details>

---

### Q49. What is a "multi-agent" system in LangGraph?
- A) Multiple users accessing the same graph
- B) Multiple specialized LLM agents collaborating through a shared graph with different roles
- C) Running the same agent on multiple servers
- D) An agent with multiple API keys

<details>
<summary>✅ Answer</summary>

**B) Multiple specialized LLM agents collaborating through a shared graph with different roles**

Example: A supervisor agent routes tasks to specialized worker agents (researcher, coder, reviewer), each implemented as a subgraph or node with its own prompt and tools.
</details>

---

### Q50. What is LangGraph Platform?
- A) A Python IDE
- B) An infrastructure for deploying, scaling, and managing LangGraph applications in production
- C) A mobile app builder
- D) A testing framework

<details>
<summary>✅ Answer</summary>

**B) An infrastructure for deploying, scaling, and managing LangGraph applications in production**

LangGraph Platform provides APIs, a task queue for background runs, a persistence layer, and a deployment server (self-hosted or LangGraph Cloud).
</details>

---

### Q51. What is LangSmith used for in the LangGraph ecosystem?
- A) Building UIs
- B) Observability, tracing, debugging, and monitoring LLM applications
- C) Training models
- D) Version control

<details>
<summary>✅ Answer</summary>

**B) Observability, tracing, debugging, and monitoring LLM applications**

LangSmith lets you trace every step of your graph execution, inspect inputs/outputs of each node, debug failures, and monitor production performance.
</details>

---

### Q52. When would you NOT recommend using LangGraph?
- A) Building a complex multi-agent system
- B) A simple single-prompt LLM call with no state or routing needed
- C) A chatbot with conversation history
- D) A workflow with conditional branching

<details>
<summary>✅ Answer</summary>

**B) A simple single-prompt LLM call with no state or routing needed**

If you're just making a single LLM call with no branching, looping, or state — a simple LangChain chain or even a direct API call is simpler and more appropriate. LangGraph adds value when you need complex orchestration.
</details>

---

### Q53. What is the `Command` object in LangGraph used for?
- A) Running shell commands
- B) Combining state updates with routing control flow in a single return from a node
- C) Sending commands to the LLM
- D) Logging commands

<details>
<summary>✅ Answer</summary>

**B) Combining state updates with routing control flow in a single return from a node**

`Command` allows a node to simultaneously update state AND specify the next node to navigate to, providing fine-grained control flow.

```python
from langgraph.types import Command

def my_node(state):
    return Command(
        update={"result": "done"},
        goto="next_node"
    )
```
</details>

---

### Q54. What is the difference between `interrupt_before` and `interrupt_after`?
- A) `interrupt_before` pauses before a node runs; `interrupt_after` pauses after a node completes
- B) They are aliases for the same feature
- C) `interrupt_before` is for debugging; `interrupt_after` is for production
- D) `interrupt_before` stops the graph permanently

<details>
<summary>✅ Answer</summary>

**A) `interrupt_before` pauses before a node runs; `interrupt_after` pauses after a node completes**

- `interrupt_before=["action"]` — Pauses BEFORE the node executes (for approval)
- `interrupt_after=["action"]` — Pauses AFTER the node executes (for review)

Both wait for human input before the graph continues.
</details>

---

### Q55. How would you test a LangGraph application without making real LLM API calls?
- A) You can't — LLM calls are required
- B) Use mock functions as nodes, replace the LLM with a deterministic stub, or use unit tests with fixture data
- C) Only test in production
- D) Use a faster LLM

<details>
<summary>✅ Answer</summary>

**B) Use mock functions as nodes, replace the LLM with a deterministic stub, or use unit tests with fixture data**

You can test graph structure, routing logic, and state management independently of the LLM by using mock node functions that return predictable data. For integration tests, use cheaper/faster models.
</details>

---

## 📊 Score Card

| Section | Questions | Your Score |
|---------|-----------|------------|
| ⭐ Basic | Q1–Q20 | __ / 20 |
| ⭐⭐ Intermediate | Q21–Q40 | __ / 20 |
| ⭐⭐⭐ Advanced | Q41–Q55 | __ / 15 |
| **Total** | **55** | **__ / 55** |

### Grading
- **50–55**: 🏆 Expert — You're interview-ready!
- **40–49**: 🥈 Strong — Review the ones you missed
- **30–39**: 🥉 Good foundation — Focus on intermediate & advanced sections
- **Below 30**: 📖 Keep studying — Revisit the [Q&A Explanations](./02_QnA.md)

---

> ⬅️ [Back to Main Guide](./README.md) | ➡️ [Next: Q&A Explanations](./02_QnA.md)
