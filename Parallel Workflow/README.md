# ⚡ Parallel Workflow

> Parallel workflows execute **multiple nodes at the same time**. Unlike sequential workflows where nodes run one after another, parallel workflows fan out from START to multiple nodes simultaneously, and then fan back in to a single node that collects the results.

---

## 📁 Files

| File | Description |
|------|-------------|
| `Parallel Workflow.py` | Cricket Player Stats — parallel stat calculations |
| `Parallel Workflow 1.py` | Structured LLM Output — essay evaluation with Pydantic |
| `Parallel Workflow 2.py` | UPSE Essay Evaluator — full parallel evaluation pipeline with LLM |

---

## 📄 File 1: `Parallel Workflow.py` — Cricket Player Stats

### What We Did
- Built a **parallel workflow** that calculates three cricket statistics **simultaneously** and then generates a summary.
- Defined a `PlayerState` with: `runs`, `balls`, `fours`, `sixes`, `sr`, `bpb`, `bp`, and `summary`.
- **Three parallel nodes** (all run at the same time):
  - `strike_rate` → Calculates `(runs / balls) × 100`
  - `balls_per_boundary` → Calculates `balls / (fours + sixes)`
  - `boundary_percentage` → Calculates `((fours + sixes) / runs) × 100`
- **One aggregator node**:
  - `player_summary` → Reads all three computed values from state and generates a formatted summary.
- **Important lesson learned**: In LangGraph, every node function **must return a `dict`** (partial state update). Returning a raw value like `float` causes `InvalidUpdateError`.

### Graph Flow
```
                    ┌──────────────────┐
                ┌──→│   strike_rate    │──┐
                │   └──────────────────┘  │
┌───────┐       │   ┌──────────────────┐  │   ┌────────────────┐      ┌─────┐
│ START │───────┼──→│balls_per_boundary│──┼──→│ player_summary │ ───→ │ END │
└───────┘       │   └──────────────────┘  │   └────────────────┘      └─────┘
                │   ┌──────────────────┐  │
                └──→│boundary_percentage──┘
                    └──────────────────┘
```

### Sample Output
```
Calculating strike rate...
Calculating balls per boundary...
Calculating boundary percentage...
Generating player summary...
{'runs': 100, 'balls': 40, 'fours': 10, 'sixes': 10, 'sr': 250.0, 'bpb': 2.0, 'bp': 20.0, 'summary': '...'}
```

---

## 📄 File 2: `Parallel Workflow 1.py` — Structured LLM Output

### What We Did
- Demonstrated how to get **structured output** from the LLM using **Pydantic BaseModel**.
- Defined a `UPSEState` (Pydantic model) with:
  - `feedback: str` — A detailed feedback string.
  - `score: int` — A score from 0 to 10 (with validation using `ge=0, le=10`).
- Used `llm.with_structured_output(schema=UPSEState)` to force the LLM to return a Pydantic object instead of raw text.
- The LLM evaluates a pre-defined essay on "AI in India" based on 10 criteria (content, clarity, originality, etc.).
- The response is a **Pydantic object** — accessed via `response.feedback` and `response.score` (dot notation, NOT bracket notation).
- This is **not a graph workflow** — it's a standalone script that shows how structured output works before using it in a graph.

### Key Lesson
```python
# ✅ Correct — Pydantic object uses dot notation
response.feedback
response.score

# ❌ Wrong — Pydantic objects are NOT dicts
response['feedback']  # TypeError: 'UPSEState' object is not subscriptable
```

---

## 📄 File 3: `Parallel Workflow 2.py` — UPSE Essay Evaluator

### What We Did
- Built a **full parallel evaluation pipeline** that evaluates an essay on three dimensions simultaneously using LLM, then aggregates results.
- **Structured output** (`ResponseState` Pydantic model) ensures the LLM returns a `feedback` string and a `score` integer.
- Defined `UPSEState` (TypedDict) with:
  - `essay` — The input essay text
  - `language_feedback`, `analysis_feedback`, `clarity_feedback` — Individual evaluation results
  - `individual_scores: Annotated[List[int], operator.add]` — Scores are **appended** (not replaced) using the `operator.add` reducer
  - `overall_feedback` — Combined final feedback
  - `overall_score` — Average of all individual scores
- **Three parallel evaluator nodes** (all run simultaneously):
  - `evaluate_language` → Evaluates language quality (grammar, vocabulary, fluency)
  - `evaluate_analysis` → Evaluates depth of analysis and argument strength
  - `evaluate_thought` → Evaluates clarity of thought and logical flow
- **One aggregator node**:
  - `final_evaluation` → Collects all three feedbacks, asks LLM for overall feedback, and calculates the average score.
- Used `operator.add` as the **reducer for `individual_scores`** — this is how you aggregate list values from parallel nodes in LangGraph.

### Graph Flow
```
                    ┌─────────────────────┐
                ┌──→│  evaluate_language  │──┐
                │   └─────────────────────┘  │
┌───────┐       │   ┌─────────────────────┐  │   ┌──────────────────┐      ┌─────┐
│ START │───────┼──→│ evaluate_analysis   │──┼──→│ final_evaluation │ ───→ │ END │
└───────┘       │   └─────────────────────┘  │   └──────────────────┘      └─────┘
                │   ┌─────────────────────┐  │
                └──→│  evaluate_thought   │──┘
                    └─────────────────────┘
```

### Important Lessons Learned

| Mistake | Fix |
|---------|-----|
| Using `{}` (set) for prompt messages | Use `[]` (list) — sets are unordered and invalid |
| Using `response['feedback']` | Use `response.feedback` — Pydantic uses dot notation |
| Returning a key not in state (`thought_feedback`) | Make sure returned keys match `TypedDict` definition (`clarity_feedback`) |

---

## 🔑 Key Concepts Learned

| Concept | What It Means |
|---------|---------------|
| **Parallel Execution** | Multiple nodes run at the same time (fan-out from START) |
| **Fan-out / Fan-in** | START fans out to multiple nodes → they fan back into one aggregator |
| **`operator.add` reducer** | Appends list items from parallel nodes instead of overwriting |
| **Structured Output** | Using Pydantic `BaseModel` to force LLM to return typed data |
| **`with_structured_output()`** | LangChain method that wraps an LLM to return Pydantic objects |
| **Nodes must return `dict`** | Every node must return a dictionary — never raw values |

---

## ▶️ How to Run

```bash
# Activate virtual environment
.\langvenv\Scripts\Activate.ps1

# Run any of the files
python "Parallel Workflow/Parallel Workflow.py"
python "Parallel Workflow/Parallel Workflow 1.py"
python "Parallel Workflow/Parallel Workflow 2.py"
```

> **Note:** Make sure your `.env` file has the `GROQ_API_KEY` set.
