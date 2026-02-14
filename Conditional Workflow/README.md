# 🔀 Conditional Workflow

> Conditional workflows use **`add_conditional_edges()`** to route the execution to different nodes based on the output of a routing function. Unlike sequential workflows (fixed path) or parallel workflows (fan-out), conditional workflows **choose a path at runtime** based on the current state.

---

## 📁 Files

| File | Description |
|------|-------------|
| `Conditional Workflow.py` | Quadratic Equation Solver — routes based on discriminant value |
| `Conditional Workflow 1.py` | Voter Eligibility Checker — multi-step conditional validation |
| `Conditional Workflow 2.py` | Medical Report Analyzer — LLM-powered sentiment routing with structured output |

---

## 📄 File 1: `Conditional Workflow.py` — Quadratic Equation Solver

### What We Did
- Built a workflow that solves a **quadratic equation** `ax² + bx + c = 0` by computing the discriminant (`D = b² - 4ac`) and routing to different nodes based on its value.
- Defined a `QState` with: `a`, `b`, `c` (coefficients), `equation`, `d` (discriminant), and `result`.
- **Node 1 (`show_equation`)**: Formats and displays the equation.
- **Node 2 (`calculate_d`)**: Computes the discriminant `D = b² - 4ac`.
- **Conditional routing (`check_d`)**: Based on the discriminant:
  - `D > 0` → **`real_roots`** — Two distinct real roots using the quadratic formula.
  - `D == 0` → **`repeated_roots`** — One repeated root: `x = -b / 2a`.
  - `D < 0` → **`no_real_roots`** — No real solutions exist.
- This is a **pure math** workflow — no LLM is used. It demonstrates conditional routing with simple logic.

### Graph Flow
```
┌───────┐      ┌────────────────┐      ┌─────────────┐
│ START │ ───→ │ show_equation  │ ───→ │ calculate_d │
└───────┘      └────────────────┘      └──────┬──────┘
                                              │
                                    ┌─────────┼─────────┐
                                    ▼         ▼         ▼
                              ┌──────────┐ ┌────────┐ ┌──────────┐
                   (D > 0)    │real_roots│ │repeated│ │no_real   │  (D < 0)
                              │          │ │_roots  │ │_roots    │
                              └────┬─────┘ └───┬────┘ └────┬─────┘
                                   │           │           │
                                   └─────────┬─┘───────────┘
                                             ▼
                                          ┌─────┐
                                          │ END │
                                          └─────┘
```

### Example
```python
# Input: 2x² + 4x + 8 → D = 16 - 64 = -48 (negative)
app.invoke({"a": 2, "b": 4, "c": 8})
# Output: "The roots are not real"
```

---

## 📄 File 2: `Conditional Workflow 1.py` — Voter Eligibility Checker

### What We Did
- Built a **multi-step conditional validation** workflow that checks whether a citizen is eligible to vote in Indian elections.
- Three eligibility criteria are checked **sequentially**, each with a conditional exit:
  1. **Age** — Must be 18 or above.
  2. **Citizenship** — Must be an Indian citizen.
  3. **Criminal Record** — Must have no criminal record.
- If any check fails, the workflow **exits early** to a rejection node with a specific reason. If all checks pass, the voter is approved and assigned a Voter ID.
- Uses **3 chained conditional edges** — this shows how you can build a decision tree using LangGraph.
- Includes **4 test cases** covering all branches (eligible, underage, non-citizen, criminal record).

### Graph Flow
```
┌───────┐      ┌──────────────┐      ┌────────────┐
│ START │ ───→ │ collect_info │ ───→ │ verify_age │
└───────┘      └──────────────┘      └─────┬──────┘
                                           │
                              ┌────────────┼────────────┐
                              ▼                         ▼
                    ┌──────────────────┐      ┌─────────────────┐
         (age ≥ 18) │verify_citizenship│      │ reject_underage │ → END
                    └────────┬─────────┘      └─────────────────┘
                             │
                ┌────────────┼────────────┐
                ▼                         ▼
      ┌────────────────────┐   ┌──────────────────┐
      │verify_criminal_    │   │reject_non_citizen│ → END
      │      record        │   └──────────────────┘
      └────────┬───────────┘
               │
      ┌────────┼────────┐
      ▼                 ▼
┌──────────────┐  ┌───────────────┐
│approve_voter │  │reject_criminal│ → END
└──────┬───────┘  └───────────────┘
       ▼
    ┌─────┐
    │ END │
    └─────┘
```

### Test Cases

| # | Name | Age | Citizen | Criminal | Result |
|---|------|-----|---------|----------|--------|
| 1 | Shafi Amirulla | 25 | ✅ | ❌ | ✅ Approved |
| 2 | Rahul Kumar | 16 | ✅ | ❌ | ❌ Underage |
| 3 | John Smith | 30 | ❌ | ❌ | ❌ Non-citizen |
| 4 | Vijay Mallya | 55 | ✅ | ✅ | ❌ Criminal record |

---

## 📄 File 3: `Conditional Workflow 2.py` — Medical Report Analyzer

### What We Did
- Built an **LLM-powered conditional workflow** that analyzes a medical diagnosis report and responds differently based on the sentiment.
- Uses **two Pydantic schemas for structured output**:
  - `SentimentSchema` — Forces the LLM to classify sentiment as `positive`, `negative`, or `neutral`.
  - `DiagnosisSchema` — Forces the LLM to return `issue_type` (acute/chronic), `tone` (angry/happy/sad/neutral), and `urgency` (low/medium/high).
- **Workflow steps:**
  1. `find_sentiment` → LLM classifies the report sentiment using structured output.
  2. Conditional routing (`check_sentiment`):
     - **Positive** → `positive_report` → Generates a warm thank-you message with health tips.
     - **Negative** → `run_diagnosis` → LLM extracts issue type, tone, and urgency → `negative_report` → Generates empathetic response with medication suggestions.
     - **Neutral** → `neutral_report` → Generates a neutral acknowledgment.
- The negative path has an **extra sequential step** — diagnosis is run first, then its results feed into the final response. This shows how you can combine conditional routing with sequential chaining.

### Graph Flow
```
┌───────┐      ┌────────────────┐
│ START │ ───→ │ find_sentiment │
└───────┘      └───────┬────────┘
                       │
           ┌───────────┼───────────┐
           ▼           ▼           ▼
   ┌───────────────┐ ┌──────────────┐ ┌────────────────┐
   │positive_report│ │run_diagnosis │ │ neutral_report │
   └───────┬───────┘ └──────┬───────┘ └───────┬────────┘
           │                ▼                  │
           │       ┌─────────────────┐         │
           │       │ negative_report │         │
           │       └───────┬─────────┘         │
           │               │                   │
           └───────────┬───┘───────────────────┘
                       ▼
                    ┌─────┐
                    │ END │
                    └─────┘
```

### Key Features
- **Structured Output with Pydantic** — LLM is forced to return data in a specific schema.
- **`Literal` types** — Restrict values to a set of options (e.g., `Literal['positive', 'negative', 'neutral']`).
- **`model_dump()`** — Converts Pydantic object to a dictionary for storing in TypedDict state.
- **Conditional + Sequential** — The negative path chains two nodes (`run_diagnosis` → `negative_report`).

---

## 🔑 Key Concepts Learned

| Concept | What It Means |
|---------|---------------|
| **`add_conditional_edges()`** | Adds an edge where the next node is determined at runtime by a routing function |
| **Routing Function** | A function that takes the state and returns the **name** of the next node as a string |
| **Early Exit** | If a condition fails, the workflow can exit to a terminal node without running remaining checks |
| **Chained Conditionals** | Multiple conditional edges in sequence — each check gates the next step |
| **Structured Output** | Using Pydantic `BaseModel` + `Literal` to force LLM to return specific typed data |
| **`model_dump()`** | Converts a Pydantic object to a plain dictionary |

### How `add_conditional_edges()` Works

```python
# Syntax:
graph.add_conditional_edges(
    source_node,       # The node AFTER which routing happens
    routing_function,  # Function that returns the name of the next node
    possible_targets   # List or dict of possible target nodes
)

# Example — list form:
graph.add_conditional_edges("calculate_d", check_d, ["real_roots", "repeated_roots", "no_real_roots"])

# Example — dict form (map routing function return → node name):
graph.add_conditional_edges("find_sentiment", check_sentiment, {
    'positive_report': 'positive_report',
    'run_diagnosis': 'run_diagnosis',
    'neutral_report': 'neutral_report'
})
```

---

## ▶️ How to Run

```bash
# Activate virtual environment
.\langvenv\Scripts\Activate.ps1

# Run any of the files
python "Conditional Workflow/Conditional Workflow.py"
python "Conditional Workflow/Conditional Workflow 1.py"
python "Conditional Workflow/Conditional Workflow 2.py"
```

> **Note:** Make sure your `.env` file has the `GROQ_API_KEY` set.
