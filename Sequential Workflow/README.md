# 🔗 Sequential Workflow

> Sequential workflows execute nodes **one after another** in a fixed order. The output of one node becomes the input for the next. This is the simplest type of LangGraph workflow.

---

## 📁 Files

| File | Description |
|------|-------------|
| `Sequential Workflow 1.py` | Simple single-node LLM query |
| `Sequential Workflow.py` | BMI Calculator — two sequential nodes |
| `Sequential Workflow 2.py` | Blog Post Generator — three-step prompt chaining |

---

## 📄 File 1: `Sequential Workflow 1.py` — Simple LLM Query

### What We Did
- Created the **simplest possible LangGraph workflow** — a single node that takes a query and returns an LLM response.
- Defined an `LLMState` with two fields: `query` (input) and `response` (output).
- Built a one-node graph:
  ```
  START → llm_query → END
  ```
- The `llm_query` node sends the query to Groq with a system message ("You are a helpful assistant") and stores the response.

### Graph Flow
```
┌───────┐      ┌───────────┐      ┌─────┐
│ START │ ───→ │ llm_query │ ───→ │ END │
└───────┘      └───────────┘      └─────┘
```

---

## 📄 File 2: `Sequential Workflow.py` — BMI Calculator

### What We Did
- Built a **two-node sequential workflow** to calculate BMI and categorize it.
- Defined a `BMIState` with: `weight`, `height`, `bmi`, and `category`.
- **Node 1 (`calculate_bmi`)**: Takes weight and height from the state, calculates `BMI = weight / height²`, and stores the result.
- **Node 2 (`label_bmi`)**: Reads the BMI value and assigns a category label:
  - BMI < 18.5 → Underweight
  - BMI 18.5–24.9 → Normal weight
  - BMI 25–29.9 → Overweight
  - BMI ≥ 30 → Obesity
- This is a **pure computation** workflow — no LLM is used. It shows that LangGraph nodes can run any Python logic, not just LLM calls.

### Graph Flow
```
┌───────┐      ┌───────────────┐      ┌───────────┐      ┌─────┐
│ START │ ───→ │ calculate_bmi │ ───→ │ label_bmi │ ───→ │ END │
└───────┘      └───────────────┘      └───────────┘      └─────┘
```

### Sample Output
```
Processing...
Weight: 70
Height: 1.75
Calculating BMI...
BMI: 22.857142857142858
Labeling BMI...
Category: Normal weight
{'weight': 70, 'height': 1.75, 'bmi': 22.857142857142858, 'category': 'Normal weight'}
```

---

## 📄 File 3: `Sequential Workflow 2.py` — Blog Post Generator (Prompt Chaining)

### What We Did
- Implemented a **prompt chaining** workflow — a complex task (writing a blog post) is broken into 3 simpler sequential prompts.
- Defined a `BlogState` with: `topic`, `outline`, `draft`, and `final_post`.
- **Node 1 (`generate_outline`)**: Takes the topic and asks the LLM to generate a structured blog outline.
- **Node 2 (`write_draft`)**: Takes the outline from Node 1 and asks the LLM to write a full blog draft (~300 words).
- **Node 3 (`polish_and_summarize`)**: Takes the draft from Node 2 and asks the LLM to polish it for clarity, grammar, and flow, and add a summary.
- Each node's output feeds directly into the next node — this is classic **prompt chaining**.

### Graph Flow
```
┌───────┐      ┌──────────────────┐      ┌─────────────┐      ┌──────────────────────┐      ┌─────┐
│ START │ ───→ │ generate_outline │ ───→ │ write_draft │ ───→ │ polish_and_summarize │ ───→ │ END │
└───────┘      └──────────────────┘      └─────────────┘      └──────────────────────┘      └─────┘
```

---

## 🔑 Key Concepts Learned

| Concept | What It Means |
|---------|---------------|
| **Sequential Execution** | Nodes run one after another in a fixed order |
| **Prompt Chaining** | Breaking a complex task into a sequence of simpler prompts |
| **State Passing** | Each node reads from and writes to the shared state |
| **`add_edge(A, B)`** | Connects node A to node B — A runs first, then B |
| **No LLM Required** | Nodes can run pure Python logic (e.g., BMI calculation) |

---

## ▶️ How to Run

```bash
# Activate virtual environment
.\langvenv\Scripts\Activate.ps1

# Run any of the files
python "Sequential Workflow/Sequential Workflow 1.py"
python "Sequential Workflow/Sequential Workflow.py"
python "Sequential Workflow/Sequential Workflow 2.py"
```

> **Note:** Make sure your `.env` file has the `GROQ_API_KEY` set.
