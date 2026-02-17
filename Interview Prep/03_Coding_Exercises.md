# 💻 LangGraph — Coding Exercises

> Hands-on coding problems with full solutions. Practice writing LangGraph code from scratch.
> **Try solving each problem before looking at the solution!**

---

## 📌 How to Use
1. Read the problem statement and requirements
2. Write your solution on paper or in an editor
3. Compare with the provided solution
4. Run the code in your LangGraph project to verify

---

## ⭐ Beginner Exercises

---

### Exercise 1: Hello LangGraph — Your First Graph

**Problem:** Create a LangGraph application with a single node that takes a `name` in the state and returns a greeting message `"Hello, {name}! Welcome to LangGraph."` Store the greeting in a `response` state key.

<details>
<summary>💡 Hint</summary>
Define a TypedDict with `name` and `response` fields. Create one node function. Connect START → node → END.
</details>

<details>
<summary>✅ Solution</summary>

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    name: str
    response: str

def greet(state: State) -> dict:
    return {"response": f"Hello, {state['name']}! Welcome to LangGraph."}

graph = StateGraph(State)
graph.add_node("greet", greet)
graph.add_edge(START, "greet")
graph.add_edge("greet", END)

app = graph.compile()
result = app.invoke({"name": "Alice"})
print(result["response"])
# Output: Hello, Alice! Welcome to LangGraph.
```

**Key concepts:** TypedDict, add_node, add_edge, START, END, compile, invoke.
</details>

---

### Exercise 2: Two-Node Sequential Pipeline

**Problem:** Build a graph with two nodes:
1. `calculate` — Takes `celsius` from state, converts to Fahrenheit using `F = C × 9/5 + 32`
2. `format_result` — Takes the `fahrenheit` value and creates a formatted string: `"{celsius}°C = {fahrenheit}°F"`

<details>
<summary>✅ Solution</summary>

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    celsius: float
    fahrenheit: float
    result: str

def calculate(state: State) -> dict:
    f = state["celsius"] * 9 / 5 + 32
    return {"fahrenheit": f}

def format_result(state: State) -> dict:
    return {"result": f"{state['celsius']}°C = {state['fahrenheit']}°F"}

graph = StateGraph(State)
graph.add_node("calculate", calculate)
graph.add_node("format_result", format_result)
graph.add_edge(START, "calculate")
graph.add_edge("calculate", "format_result")
graph.add_edge("format_result", END)

app = graph.compile()
result = app.invoke({"celsius": 100})
print(result["result"])
# Output: 100°C = 212.0°F
```
</details>

---

### Exercise 3: Three-Node Prompt Chaining with LLM

**Problem:** Create a 3-node sequential workflow for generating a product description:
1. `generate_features` — Ask LLM to list 3 key features of the product
2. `write_description` — Ask LLM to write a marketing description using those features
3. `create_tagline` — Ask LLM to create a catchy tagline based on the description

State should have: `product`, `features`, `description`, `tagline`

<details>
<summary>✅ Solution</summary>

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile")

class State(TypedDict):
    product: str
    features: str
    description: str
    tagline: str

def generate_features(state: State) -> dict:
    msg = llm.invoke([HumanMessage(
        content=f"List 3 key features of {state['product']}. Be brief."
    )])
    return {"features": msg.content}

def write_description(state: State) -> dict:
    msg = llm.invoke([HumanMessage(
        content=f"Write a 2-sentence marketing description for {state['product']} "
                f"based on these features: {state['features']}"
    )])
    return {"description": msg.content}

def create_tagline(state: State) -> dict:
    msg = llm.invoke([HumanMessage(
        content=f"Create a catchy tagline for: {state['description']}"
    )])
    return {"tagline": msg.content}

graph = StateGraph(State)
graph.add_node("generate_features", generate_features)
graph.add_node("write_description", write_description)
graph.add_node("create_tagline", create_tagline)
graph.add_edge(START, "generate_features")
graph.add_edge("generate_features", "write_description")
graph.add_edge("write_description", "create_tagline")
graph.add_edge("create_tagline", END)

app = graph.compile()
result = app.invoke({"product": "wireless earbuds"})
print(f"Features: {result['features']}")
print(f"Description: {result['description']}")
print(f"Tagline: {result['tagline']}")
```
</details>

---

## ⭐⭐ Intermediate Exercises

---

### Exercise 4: Parallel Fan-Out / Fan-In

**Problem:** Build a parallel workflow that analyzes a piece of text from three perspectives simultaneously:
1. `count_words` — Count the number of words
2. `count_sentences` — Count the number of sentences (split by `.`)
3. `count_chars` — Count the number of characters

Then an `aggregate` node combines all counts into a `summary` string.

**Important:** Use a state reducer for the parallel results.

<details>
<summary>✅ Solution</summary>

```python
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    text: str
    stats: Annotated[list[str], operator.add]  # Reducer!
    summary: str

def count_words(state: State) -> dict:
    count = len(state["text"].split())
    return {"stats": [f"Words: {count}"]}

def count_sentences(state: State) -> dict:
    count = len([s for s in state["text"].split(".") if s.strip()])
    return {"stats": [f"Sentences: {count}"]}

def count_chars(state: State) -> dict:
    count = len(state["text"])
    return {"stats": [f"Characters: {count}"]}

def aggregate(state: State) -> dict:
    return {"summary": " | ".join(state["stats"])}

graph = StateGraph(State)
graph.add_node("count_words", count_words)
graph.add_node("count_sentences", count_sentences)
graph.add_node("count_chars", count_chars)
graph.add_node("aggregate", aggregate)

# Fan-out
graph.add_edge(START, "count_words")
graph.add_edge(START, "count_sentences")
graph.add_edge(START, "count_chars")

# Fan-in
graph.add_edge("count_words", "aggregate")
graph.add_edge("count_sentences", "aggregate")
graph.add_edge("count_chars", "aggregate")
graph.add_edge("aggregate", END)

app = graph.compile()
result = app.invoke({"text": "LangGraph is great. It builds workflows. I love it."})
print(result["summary"])
# Output: Words: 10 | Sentences: 3 | Characters: 51
```

**Key concept:** Without `Annotated[list[str], operator.add]`, only the last parallel node's result would be kept.
</details>

---

### Exercise 5: Conditional Routing — Grade Classifier

**Problem:** Build a conditional workflow that takes a student's `score` (0–100) and routes to:
- `grade_a` if score ≥ 90
- `grade_b` if score ≥ 80
- `grade_c` if score ≥ 70
- `grade_fail` otherwise

Each grade node sets a `grade` and `message` in the state.

<details>
<summary>✅ Solution</summary>

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    score: int
    grade: str
    message: str

def classify(state: State) -> dict:
    return {}  # Just passes through to routing

def grade_a(state: State) -> dict:
    return {"grade": "A", "message": f"Excellent! Score: {state['score']}"}

def grade_b(state: State) -> dict:
    return {"grade": "B", "message": f"Good job! Score: {state['score']}"}

def grade_c(state: State) -> dict:
    return {"grade": "C", "message": f"Satisfactory. Score: {state['score']}"}

def grade_fail(state: State) -> dict:
    return {"grade": "F", "message": f"Needs improvement. Score: {state['score']}"}

def route_grade(state: State) -> str:
    score = state["score"]
    if score >= 90:
        return "a"
    elif score >= 80:
        return "b"
    elif score >= 70:
        return "c"
    return "fail"

graph = StateGraph(State)
graph.add_node("classify", classify)
graph.add_node("grade_a", grade_a)
graph.add_node("grade_b", grade_b)
graph.add_node("grade_c", grade_c)
graph.add_node("grade_fail", grade_fail)

graph.add_edge(START, "classify")
graph.add_conditional_edges("classify", route_grade, {
    "a": "grade_a",
    "b": "grade_b",
    "c": "grade_c",
    "fail": "grade_fail"
})
graph.add_edge("grade_a", END)
graph.add_edge("grade_b", END)
graph.add_edge("grade_c", END)
graph.add_edge("grade_fail", END)

app = graph.compile()
print(app.invoke({"score": 95}))  # Grade A
print(app.invoke({"score": 65}))  # Grade F
```
</details>

---

### Exercise 6: Iterative Loop — Password Validator

**Problem:** Build a loop that generates random passwords and checks if they meet criteria:
- At least 12 characters
- Contains uppercase, lowercase, digit, and special character

The graph should loop (max 5 attempts) until a valid password is generated.

<details>
<summary>✅ Solution</summary>

```python
import random
import string
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    password: str
    is_valid: bool
    attempts: int

def generate_password(state: State) -> dict:
    length = random.randint(8, 16)
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(random.choice(chars) for _ in range(length))
    return {"password": password, "attempts": state.get("attempts", 0) + 1}

def validate_password(state: State) -> dict:
    pw = state["password"]
    checks = [
        len(pw) >= 12,
        any(c.isupper() for c in pw),
        any(c.islower() for c in pw),
        any(c.isdigit() for c in pw),
        any(c in "!@#$%^&*" for c in pw)
    ]
    return {"is_valid": all(checks)}

def route(state: State) -> str:
    if state["is_valid"]:
        return "done"
    if state["attempts"] >= 5:
        return "done"  # Give up after 5 attempts
    return "retry"

graph = StateGraph(State)
graph.add_node("generate", generate_password)
graph.add_node("validate", validate_password)

graph.add_edge(START, "generate")
graph.add_edge("generate", "validate")
graph.add_conditional_edges("validate", route, {
    "retry": "generate",  # Loop back
    "done": END
})

app = graph.compile()
result = app.invoke({"password": "", "is_valid": False, "attempts": 0})
print(f"Password: {result['password']}")
print(f"Valid: {result['is_valid']}")
print(f"Attempts: {result['attempts']}")
```
</details>

---

### Exercise 7: Chatbot with Memory

**Problem:** Build a simple chatbot that remembers conversation history using `MemorySaver` and `add_messages`. The bot should:
1. Accept user messages
2. Maintain conversation history across multiple invocations
3. Support multiple threads (different conversations)

<details>
<summary>✅ Solution</summary>

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile")

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chat(state: State) -> dict:
    system = SystemMessage(content="You are a friendly assistant. Keep responses brief.")
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}

graph = StateGraph(State)
graph.add_node("chat", chat)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

app = graph.compile(checkpointer=MemorySaver())

# Thread 1 — Alice's conversation
config1 = {"configurable": {"thread_id": "alice"}}
r1 = app.invoke({"messages": [HumanMessage("My name is Alice")]}, config1)
r2 = app.invoke({"messages": [HumanMessage("What is my name?")]}, config1)
print(r2["messages"][-1].content)  # Should remember "Alice"

# Thread 2 — Bob's separate conversation
config2 = {"configurable": {"thread_id": "bob"}}
r3 = app.invoke({"messages": [HumanMessage("My name is Bob")]}, config2)
r4 = app.invoke({"messages": [HumanMessage("What is my name?")]}, config2)
print(r4["messages"][-1].content)  # Should say "Bob", not "Alice"
```

**Key concepts:** `add_messages` reducer, `MemorySaver`, `thread_id` isolation.
</details>

---

## ⭐⭐⭐ Advanced Exercises

---

### Exercise 8: Debug This Broken Graph

**Problem:** The following code has **4 bugs**. Find and fix them all.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph.memory import MemorySaver  # Bug 1

llm = ChatGroq(model="llama-3.3-70b-versatile")

class State(TypedDict):
    query: str
    answer: str

def ask_llm(state):
    prompt = {  # Bug 2
        SystemMessage(content="You are helpful."),
        HumanMessage(content=state["query"])
    }
    response = llm.invoke(prompt)
    return response.content  # Bug 3

graph = StateGraph(State)
graph.add_node("ask", ask_llm)
graph.add_edge(START, "ask")
# Bug 4: missing edge to END

app = graph.compile(checkpointer=MemorySaver())
result = app.invoke({"query": "What is Python?"})
print(result["answer"])
```

<details>
<summary>✅ Solution — All 4 Bugs Fixed</summary>

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver  # Fix 1: correct import path

llm = ChatGroq(model="llama-3.3-70b-versatile")

class State(TypedDict):
    query: str
    answer: str

def ask_llm(state):
    prompt = [  # Fix 2: use list [], not set {}
        SystemMessage(content="You are helpful."),
        HumanMessage(content=state["query"])
    ]
    response = llm.invoke(prompt)
    return {"answer": response.content}  # Fix 3: return dict, not raw string

graph = StateGraph(State)
graph.add_node("ask", ask_llm)
graph.add_edge(START, "ask")
graph.add_edge("ask", END)  # Fix 4: add edge to END

app = graph.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "t1"}}  # Need config for checkpointer
result = app.invoke({"query": "What is Python?"}, config)
print(result["answer"])
```

**Bugs:**
1. Wrong import path for `MemorySaver`
2. Used `{}` (set) instead of `[]` (list) for prompt
3. Returned raw string instead of dict
4. Missing edge from "ask" to END
</details>

---

### Exercise 9: Parallel LLM Evaluation with Structured Output

**Problem:** Build a parallel graph that evaluates a restaurant review from 3 perspectives simultaneously:
1. `eval_food` — Rate food quality (0-10) with feedback
2. `eval_service` — Rate service quality (0-10) with feedback
3. `eval_ambiance` — Rate ambiance (0-10) with feedback

Use **Pydantic** for structured output. An `aggregate` node calculates the average score and provides an overall verdict.

<details>
<summary>✅ Solution</summary>

```python
from typing import TypedDict, Annotated
import operator
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile")

class Evaluation(BaseModel):
    score: int = Field(description="Score from 0 to 10")
    feedback: str = Field(description="Brief feedback")

class State(TypedDict):
    review: str
    evaluations: Annotated[list[dict], operator.add]
    overall_score: float
    verdict: str

def eval_food(state: State) -> dict:
    structured = llm.with_structured_output(Evaluation)
    result = structured.invoke(f"Rate the FOOD quality in this review (0-10): {state['review']}")
    return {"evaluations": [{"aspect": "Food", "score": result.score, "feedback": result.feedback}]}

def eval_service(state: State) -> dict:
    structured = llm.with_structured_output(Evaluation)
    result = structured.invoke(f"Rate the SERVICE quality in this review (0-10): {state['review']}")
    return {"evaluations": [{"aspect": "Service", "score": result.score, "feedback": result.feedback}]}

def eval_ambiance(state: State) -> dict:
    structured = llm.with_structured_output(Evaluation)
    result = structured.invoke(f"Rate the AMBIANCE in this review (0-10): {state['review']}")
    return {"evaluations": [{"aspect": "Ambiance", "score": result.score, "feedback": result.feedback}]}

def aggregate(state: State) -> dict:
    scores = [e["score"] for e in state["evaluations"]]
    avg = sum(scores) / len(scores)
    verdict = "Highly Recommended" if avg >= 7 else "Average" if avg >= 5 else "Not Recommended"
    return {"overall_score": avg, "verdict": verdict}

graph = StateGraph(State)
graph.add_node("eval_food", eval_food)
graph.add_node("eval_service", eval_service)
graph.add_node("eval_ambiance", eval_ambiance)
graph.add_node("aggregate", aggregate)

graph.add_edge(START, "eval_food")
graph.add_edge(START, "eval_service")
graph.add_edge(START, "eval_ambiance")
graph.add_edge("eval_food", "aggregate")
graph.add_edge("eval_service", "aggregate")
graph.add_edge("eval_ambiance", "aggregate")
graph.add_edge("aggregate", END)

app = graph.compile()
result = app.invoke({"review": "The pasta was amazing and the staff was very friendly, but the restaurant was too loud."})
for e in result["evaluations"]:
    print(f"{e['aspect']}: {e['score']}/10 — {e['feedback']}")
print(f"Overall: {result['overall_score']:.1f}/10 — {result['verdict']}")
```
</details>

---

### Exercise 10: State Inspection & Time Travel

**Problem:** Create a 3-node pipeline, run it, then:
1. Print the current state using `get_state()`
2. Print all checkpoint history using `get_state_history()`
3. Go back to the state after the first node and print it

<details>
<summary>✅ Solution</summary>

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

class State(TypedDict):
    value: int
    log: str

def step1(state: State) -> dict:
    return {"value": state["value"] + 10, "log": "step1 done"}

def step2(state: State) -> dict:
    return {"value": state["value"] * 2, "log": "step2 done"}

def step3(state: State) -> dict:
    return {"value": state["value"] - 5, "log": "step3 done"}

graph = StateGraph(State)
graph.add_node("step1", step1)
graph.add_node("step2", step2)
graph.add_node("step3", step3)
graph.add_edge(START, "step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", "step3")
graph.add_edge("step3", END)

app = graph.compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": "demo"}}

# Run the graph
result = app.invoke({"value": 5}, config)
print(f"Final result: {result}")  # value: (5+10)*2-5 = 25

# 1. Current state
current = app.get_state(config)
print(f"Current state: {current.values}")

# 2. All checkpoint history
print("\n--- Checkpoint History ---")
history = list(app.get_state_history(config))
for i, state in enumerate(history):
    print(f"  Checkpoint {i}: {state.values} (step: {state.metadata.get('step', 'N/A')})")

# 3. Time travel — go back to after step1
# History is in reverse order, so find the right checkpoint
for state in history:
    if state.values.get("log") == "step1 done":
        print(f"\nState after step1: {state.values}")
        break
```
</details>

---

### Exercise 11: Conditional + Loop — Quiz Game

**Problem:** Build an interactive quiz game graph:
1. `ask_question` — Picks a question from a predefined list
2. `check_answer` — Compares user answer to correct answer
3. **Conditional routing:** If correct → `celebrate` → END. If wrong and attempts < 3 → loop back to `ask_question`. If wrong and attempts ≥ 3 → `game_over` → END.

<details>
<summary>✅ Solution</summary>

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

QUESTIONS = [
    {"q": "What class creates a graph?", "a": "stategraph"},
    {"q": "What must nodes return?", "a": "dict"},
    {"q": "What saves state between nodes?", "a": "checkpointer"},
]

class State(TypedDict):
    question_index: int
    current_question: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    attempts: int
    result: str

def ask_question(state: State) -> dict:
    idx = state.get("question_index", 0) % len(QUESTIONS)
    q = QUESTIONS[idx]
    return {
        "current_question": q["q"],
        "correct_answer": q["a"],
        "question_index": idx
    }

def check_answer(state: State) -> dict:
    is_correct = state["user_answer"].lower().strip() == state["correct_answer"]
    return {
        "is_correct": is_correct,
        "attempts": state.get("attempts", 0) + 1
    }

def celebrate(state: State) -> dict:
    return {"result": f"🎉 Correct in {state['attempts']} attempt(s)!"}

def game_over(state: State) -> dict:
    return {"result": f"💀 Game over after {state['attempts']} attempts. Answer: {state['correct_answer']}"}

def route(state: State) -> str:
    if state["is_correct"]:
        return "win"
    if state["attempts"] >= 3:
        return "lose"
    return "retry"

graph = StateGraph(State)
graph.add_node("ask", ask_question)
graph.add_node("check", check_answer)
graph.add_node("celebrate", celebrate)
graph.add_node("game_over", game_over)

graph.add_edge(START, "ask")
graph.add_edge("ask", "check")
graph.add_conditional_edges("check", route, {
    "win": "celebrate",
    "lose": "game_over",
    "retry": "ask"
})
graph.add_edge("celebrate", END)
graph.add_edge("game_over", END)

app = graph.compile()

# Test — wrong answer
result = app.invoke({
    "question_index": 0,
    "user_answer": "stategraph",
    "attempts": 0
})
print(result["result"])
```
</details>

---

### Exercise 12: Build a ReAct-Style Tool-Calling Agent

**Problem:** Using `create_react_agent`, build an agent that has two tools:
1. `get_weather` — Returns weather for a given city
2. `calculate` — Evaluates a math expression

Then ask: "What's the weather in Tokyo, and what is 25 × 4?"

<details>
<summary>✅ Solution</summary>

```python
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile")

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""
    # Mock implementation
    weather_data = {
        "tokyo": "Sunny, 22°C",
        "london": "Cloudy, 14°C",
        "new york": "Rainy, 18°C"
    }
    return weather_data.get(city.lower(), f"Weather data not available for {city}")

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression and return the result."""
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {e}"

# Create the agent
agent = create_react_agent(llm, tools=[get_weather, calculate])

# Ask a multi-tool question
result = agent.invoke({
    "messages": [HumanMessage("What's the weather in Tokyo, and what is 25 × 4?")]
})

# Print the final response
print(result["messages"][-1].content)
```

**Key concept:** `create_react_agent` handles the tool-calling loop automatically — the LLM decides which tools to call and when to stop.
</details>

---

### Exercise 13: Extend an Existing Graph — Add a New Feature

**Problem:** You have this existing graph for a text summarizer:

```python
# Given graph: START → summarize → END
```

**Extend it** to add:
1. A `word_count` node BEFORE summarize (adds word count to state)
2. A `translate` node AFTER summarize (translates summary to Spanish)
3. A conditional edge: if word count > 100, summarize first; if ≤ 100, skip directly to translate

<details>
<summary>✅ Solution</summary>

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile")

class State(TypedDict):
    text: str
    word_count: int
    summary: str
    translated: str

def count_words(state: State) -> dict:
    return {"word_count": len(state["text"].split())}

def summarize(state: State) -> dict:
    msg = llm.invoke([HumanMessage(
        content=f"Summarize this in 2 sentences: {state['text']}"
    )])
    return {"summary": msg.content}

def translate(state: State) -> dict:
    text_to_translate = state.get("summary") or state["text"]
    msg = llm.invoke([HumanMessage(
        content=f"Translate to Spanish: {text_to_translate}"
    )])
    return {"translated": msg.content}

def route_by_length(state: State) -> str:
    return "summarize" if state["word_count"] > 100 else "skip"

graph = StateGraph(State)
graph.add_node("count_words", count_words)
graph.add_node("summarize", summarize)
graph.add_node("translate", translate)

graph.add_edge(START, "count_words")
graph.add_conditional_edges("count_words", route_by_length, {
    "summarize": "summarize",
    "skip": "translate"
})
graph.add_edge("summarize", "translate")
graph.add_edge("translate", END)

app = graph.compile()
result = app.invoke({"text": "LangGraph is an amazing framework."})
print(f"Words: {result['word_count']}, Translation: {result['translated']}")
```
</details>

---

## 📊 Exercise Tracker

| # | Exercise | Difficulty | Status |
|---|----------|------------|--------|
| 1 | Hello LangGraph | ⭐ | ☐ |
| 2 | Temperature Converter | ⭐ | ☐ |
| 3 | Product Description Chain | ⭐ | ☐ |
| 4 | Parallel Text Analysis | ⭐⭐ | ☐ |
| 5 | Grade Classifier | ⭐⭐ | ☐ |
| 6 | Password Validator Loop | ⭐⭐ | ☐ |
| 7 | Chatbot with Memory | ⭐⭐ | ☐ |
| 8 | Debug the Broken Graph | ⭐⭐⭐ | ☐ |
| 9 | Parallel LLM Evaluation | ⭐⭐⭐ | ☐ |
| 10 | State Inspection & Time Travel | ⭐⭐⭐ | ☐ |
| 11 | Quiz Game (Conditional + Loop) | ⭐⭐⭐ | ☐ |
| 12 | ReAct Tool-Calling Agent | ⭐⭐⭐ | ☐ |
| 13 | Extend an Existing Graph | ⭐⭐⭐ | ☐ |

---

> ⬅️ [Back to Main Guide](./README.md) | ⬅️ [Previous: Q&A](./02_QnA.md) | ➡️ [Next: Scenario-Based Problems](./04_Scenario_Based.md)
