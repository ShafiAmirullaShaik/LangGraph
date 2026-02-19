# 🔁 Iterative Workflow

> Iterative workflows use **loops** to repeat a set of nodes until a condition is met. Unlike sequential workflows where nodes run once in order, iterative workflows use `add_conditional_edges()` to decide whether to **loop back** to a previous node or **exit** to the next step.

---

## 📁 Files

| File | Description |
|------|-------------|
| `Iterative Workflow.py` | Simple Counter — basic loop that counts up to a target |
| `Iterative Workflow 1.py` | AI Tweet Generator — iterative generate → evaluate → optimize loop with LLM |

---

## 📄 File 1: `Iterative Workflow.py` — Simple Counter

### What We Did
- Built the **simplest possible iterative workflow** — a counter that loops until it reaches a target number.
- Defined a `CounterState` with:
  - `count: int` — the current count
  - `target: int` — the number to stop at
- **Two nodes**:
  - `add_one` → Increments `count` by 1 each iteration.
  - `done` → Prints the final count when the loop ends.
- **One routing function**:
  - `check_count` → Decides whether to loop back to `add_one` or move to `done`.
- Used `add_conditional_edges()` to create the loop — this is the **core mechanism** for iterative workflows in LangGraph.

### Graph Flow
```
┌───────┐      ┌─────────┐      ┌─────────────┐
│ START │─────→│ add_one │─────→│ check_count │
└───────┘      └─────────┘      └─────────────┘
                   ↑                    │
                   │    count < target  │
                   └────────────────────┘
                                        │
                              count >= target
                                        │
                                        ↓
                                   ┌────────┐      ┌─────┐
                                   │  done  │─────→│ END │
                                   └────────┘      └─────┘
```

### Sample Output
```
🎯 Enter a target number to count to: 5
==============================
🎯 Counting to 5
==============================
🔄 Count: 1
🔄 Count: 2
🔄 Count: 3
🔄 Count: 4
🔄 Count: 5

✅ Done! Final count: 5

📊 Final State: {'count': 5, 'target': 5}
```

---

## 📄 File 2: `Iterative Workflow 1.py` — AI Tweet Generator & Evaluator

### What We Did
- Built an **iterative LLM-powered pipeline** that generates a tweet, evaluates it, and optimizes it in a loop until the tweet is approved or the max iteration limit is reached.
- Used **Groq LLM** (`llama-3.3-70b-versatile`) for both generation and evaluation.
- Used **Pydantic structured output** (`Evaluation` model) to force the evaluator LLM to return a typed response with `evaluation` and `feedback` fields.
- Defined `PostState` (TypedDict) with:
  - `topic` — The tweet topic
  - `tweet` — The current tweet draft
  - `evaluation` — `"approved"` or `"needs_improvement"`
  - `feedback` — Evaluator's feedback on the tweet
  - `iteration` / `max_iterations` — Loop control
  - `tweet_history: Annotated[list[str], operator.add]` — All tweet versions (appended via reducer)
  - `feedback_history: Annotated[list[str], operator.add]` — All feedback entries (appended via reducer)
- **Three nodes**:
  - `generate_tweet` → Writes an original, humorous tweet on the given topic.
  - `evaluate_tweet` → A ruthless Twitter critic that scores the tweet on originality, humor, punchiness, virality, and format. Auto-rejects Q&A jokes, setup-punchline format, and tweets over 280 characters.
  - `optimize_tweet` → Rewrites the tweet based on the evaluator's feedback.
- **One routing function**:
  - `route_evaluation` → If `"approved"` or max iterations reached → END. Otherwise → loop back to `optimize_tweet`.

### Graph Flow
```
┌───────┐      ┌────────────────┐      ┌────────────────┐
│ START │─────→│ generate_tweet │─────→│ evaluate_tweet │
└───────┘      └────────────────┘      └────────────────┘
                                              │
                                   ┌──────────┴──────────┐
                                   │                     │
                              "approved"          "needs_improvement"
                            OR max iters              │
                                   │                  ↓
                                   ↓          ┌────────────────┐
                               ┌─────┐        │ optimize_tweet │
                               │ END │        └───────┬────────┘
                               └─────┘                │
                                                      │
                                   ┌──────────────────┘
                                   ↓
                           ┌────────────────┐
                           │ evaluate_tweet │ (loop back)
                           └────────────────┘
```

### Key Concepts Used

| Concept | How It's Used |
|---------|---------------|
| **Structured Output** | `llm.with_structured_output(schema=Evaluation)` forces the evaluator to return typed `evaluation` + `feedback` |
| **Pydantic BaseModel** | `Evaluation` model with `Literal["approved", "needs_improvement"]` ensures valid responses |
| **`operator.add` reducer** | `tweet_history` and `feedback_history` append across iterations instead of overwriting |
| **Conditional Edges** | `route_evaluation` decides to loop or exit based on evaluation result and iteration count |
| **Max Iteration Guard** | Prevents infinite loops — stops after `max_iterations` even if not approved |

### Sample Output
```
==================================================
FINAL TWEET: <optimized tweet text>
==================================================
EVALUATION: APPROVED
FEEDBACK: <evaluator's final feedback>
ITERATIONS: 2
--------------------------------------------------
TWEET HISTORY:
  1. <first draft>
  2. <optimized version>
--------------------------------------------------
FEEDBACK HISTORY:
  1. <first round feedback>
  2. <second round feedback>
==================================================
```

---

## 🔑 Key Concepts Learned

| Concept | What It Means |
|---------|---------------|
| **Iterative Workflow** | A workflow where nodes can loop back to previous nodes until a condition is met |
| **`add_conditional_edges()`** | The LangGraph method that enables branching and looping based on a routing function |
| **Routing Function** | A plain Python function that returns the name of the next node to execute |
| **Loop Guard** | Using a counter (`iteration` / `max_iterations`) to prevent infinite loops |
| **`operator.add` reducer** | Appends list values across iterations instead of overwriting — essential for tracking history |
| **Structured Output** | Using Pydantic `BaseModel` + `with_structured_output()` to get typed LLM responses |

---

## ▶️ How to Run

```bash
# Activate virtual environment
.\langvenv\Scripts\Activate.ps1

# Run the simple counter
python "Iterative Workflow/Iterative Workflow.py"

# Run the AI tweet generator
python "Iterative Workflow/Iterative Workflow 1.py"
```

> **Note:** For `Iterative Workflow 1.py`, make sure your `.env` file has the `GROQ_API_KEY` set.
