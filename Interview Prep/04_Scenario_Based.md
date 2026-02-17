# 🌍 LangGraph — Scenario-Based Problems

> Real-world interview scenarios covering system design, debugging, architecture decisions, and production challenges.
> These simulate the kind of open-ended questions asked in senior-level interviews.

---

## 📌 How to Use
1. Read the scenario carefully
2. Sketch your solution (graph design, state schema, node breakdown)
3. Compare with the provided approach
4. Think about trade-offs and alternatives

---

## 🏗️ System Design Scenarios

---

### Scenario 1: Customer Support Chatbot with Escalation

**Problem:** Design a LangGraph-based customer support chatbot for an e-commerce company that:
- Answers simple FAQs (shipping, returns, hours) automatically
- Classifies complex issues and routes to the right department (billing, technical, complaints)
- Escalates to a human agent if the bot can't resolve after 3 attempts
- Maintains conversation history per customer

**Design your:** State schema, graph nodes, edges, and escalation strategy.

<details>
<summary>✅ Approach</summary>

**State:**
```python
class SupportState(TypedDict):
    messages: Annotated[list, add_messages]
    category: str          # faq, billing, technical, complaint
    resolved: bool
    attempts: int
    escalated: bool
    customer_id: str
```

**Graph Flow:**
```
START → classify_intent
  → [faq] → handle_faq → check_resolved
  → [billing] → handle_billing → check_resolved
  → [technical] → handle_technical → check_resolved
  → [complaint] → handle_complaint → check_resolved

check_resolved:
  → [resolved] → END
  → [not resolved, attempts < 3] → rephrase_response → classify_intent (loop)
  → [not resolved, attempts ≥ 3] → escalate_to_human → END
```

**Key Design Decisions:**
- **Structured output** for classification ensures reliable routing
- **Loop with max attempts** prevents infinite retries
- **Checkpointer** with `thread_id=customer_id` maintains per-customer history
- **Human-in-the-loop** via `interrupt_before=["escalate_to_human"]`
- **Production:** Use `PostgresSaver` for durable state across server restarts
</details>

---

### Scenario 2: Multi-Agent Research Assistant

**Problem:** Design a research assistant that, given a topic:
1. A **Researcher agent** searches for relevant information (3 sources in parallel)
2. A **Writer agent** composes a comprehensive report
3. A **Reviewer agent** evaluates quality and either approves or requests revisions
4. Maximum 2 revision cycles

**Design the multi-agent architecture using LangGraph.**

<details>
<summary>✅ Approach</summary>

**Architecture: Supervisor + 3 Worker Agents**

```
START → supervisor → researcher (subgraph)
                       ├── search_source_1 ─┐
                       ├── search_source_2 ─┼─ merge_results
                       └── search_source_3 ─┘
       supervisor → writer (subgraph)
                       └── compose_report
       supervisor → reviewer (subgraph)
                       └── evaluate_quality
         → [approved] → END
         → [revise, cycle < 2] → writer → reviewer (loop)
         → [revise, cycle ≥ 2] → finalize → END
```

**State:**
```python
class ResearchState(TypedDict):
    topic: str
    sources: Annotated[list[str], operator.add]
    report: str
    review_feedback: str
    quality_score: float
    revision_cycle: int
    status: str  # "researching", "writing", "reviewing", "done"
```

**Key Design Decisions:**
- **Subgraphs** for each agent allow independent development and testing
- **Parallel search** (fan-out) within the researcher subgraph
- **Iterative loop** between writer and reviewer (max 2 cycles)
- **Each agent** has its own system prompt and tools
</details>

---

### Scenario 3: RAG Pipeline with Hallucination Detection

**Problem:** Design a RAG (Retrieval Augmented Generation) pipeline that:
- Retrieves documents from a vector store
- Generates an answer grounded in the retrieved documents
- Detects hallucinations (answer claims not supported by documents)
- Re-generates if hallucinations are detected (max 2 retries)
- Returns "I don't have enough information" if the answer can't be grounded

<details>
<summary>✅ Approach</summary>

**Graph:**
```
START → retrieve → rank_relevance
  → [relevant docs found] → generate_answer → check_grounding
       → [grounded] → format_response → END
       → [hallucination, retries < 2] → generate_answer (loop with stricter prompt)
       → [hallucination, retries ≥ 2] → fallback_response → END
  → [no relevant docs] → fallback_response → END
```

**State:**
```python
class RAGState(TypedDict):
    query: str
    documents: list[dict]
    relevance_scores: list[float]
    answer: str
    grounding_check: bool
    hallucinated_claims: list[str]
    retries: int
    final_response: str
```

**Key Design Decisions:**
- **Structured output** for grounding check returns `{"grounded": bool, "claims": list[str]}`
- **Progressive prompting** — Each retry uses a stricter prompt: "Only use facts from these documents"
- **Graceful fallback** — Rather than giving a wrong answer, say "I don't have enough information"
- **Relevance threshold** — Skip generation entirely if no relevant documents found
</details>

---

### Scenario 4: E-Commerce Order Processing Pipeline

**Problem:** Design an order processing system that:
1. Validates the order (stock check, price validation)
2. Processes payment (in parallel: fraud check + payment gateway)
3. Routes based on payment result (success → fulfill, failure → notify customer)
4. Sends confirmation and updates inventory

**This must be fault-tolerant — crashes shouldn't lose order progress.**

<details>
<summary>✅ Approach</summary>

**Graph:**
```
START → validate_order
  → [invalid] → reject_order → END
  → [valid] → ┌─ fraud_check     ─┐
               └─ process_payment ─┘ → payment_result
  → [payment success] → fulfill_order → send_confirmation → update_inventory → END
  → [payment failed] → notify_customer → END
  → [fraud detected] → flag_order → notify_security → END
```

**State:**
```python
class OrderState(TypedDict):
    order_id: str
    items: list[dict]
    payment_info: dict
    validation_result: str
    fraud_result: Annotated[list[str], operator.add]
    payment_result: Annotated[list[str], operator.add]
    fulfillment_status: str
    error: str
```

**Key Design Decisions:**
- **Parallel fraud check + payment** — Reduces latency
- **Checkpointer (PostgresSaver)** — Ensures crash recovery; no order is lost
- **Conditional routing** at every decision point
- **Idempotent nodes** — Each node can be safely re-run (critical for crash recovery)
- **Human-in-the-loop** — `interrupt_before=["flag_order"]` for fraud cases
</details>

---

## 🐛 Debugging Scenarios

---

### Scenario 5: The Silent State Bug

**Problem:** A developer built a parallel workflow with 3 nodes writing scores. Only one score appears in the final state. What's wrong and how do you fix it?

```python
class State(TypedDict):
    text: str
    scores: list[int]  # ← Suspicious

# Three parallel nodes each return: {"scores": [85]}
```

<details>
<summary>✅ Diagnosis & Fix</summary>

**Problem:** No state reducer. Without `Annotated[list[int], operator.add]`, the last parallel node to finish overwrites the others.

**Fix:**
```python
from typing import Annotated
import operator

class State(TypedDict):
    text: str
    scores: Annotated[list[int], operator.add]  # ← Add reducer
```

**Lesson:** Always use reducers when parallel nodes write to the same state key.
</details>

---

### Scenario 6: The Infinite Loop

**Problem:** A developer's graph runs forever and eventually hits `GraphRecursionError`. The graph architecture:
```
generate → evaluate → (retry → generate OR done → END)
```

The routing function:
```python
def route(state):
    if state["score"] > 80:
        return "done"
    return "retry"
```

The `score` never reaches 80. What's wrong and how do you fix it?

<details>
<summary>✅ Diagnosis & Fix</summary>

**Problem:** No termination condition besides the score threshold. If the LLM consistently generates low-quality output, the loop runs forever.

**Fix — Add a max-retry counter:**
```python
def route(state):
    if state["score"] > 80:
        return "done"
    if state["attempts"] >= 5:  # ← Safety exit
        return "done"
    return "retry"
```

**Also consider:** Lowering the threshold after each retry, or using progressive prompting (more specific instructions each time).
</details>

---

### Scenario 7: Memory Not Working Across Invocations

**Problem:** A developer built a chatbot but it doesn't remember previous messages. Code:

```python
app = graph.compile()  # No checkpointer!
result = app.invoke({"messages": [HumanMessage("My name is Alice")]})
result = app.invoke({"messages": [HumanMessage("What's my name?")]})
# LLM says "I don't know your name"
```

<details>
<summary>✅ Diagnosis & Fix</summary>

**Two problems:**

1. **No checkpointer** — Without a checkpointer, state is discarded after each invocation
2. **No thread_id** — Even with a checkpointer, you need a `thread_id` to identify the conversation

**Fix:**
```python
from langgraph.checkpoint.memory import MemorySaver

app = graph.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "alice_chat"}}
app.invoke({"messages": [HumanMessage("My name is Alice")]}, config)
app.invoke({"messages": [HumanMessage("What's my name?")]}, config)
# Now it remembers!
```
</details>

---

### Scenario 8: Pydantic Structured Output Crash

**Problem:** A node gets a `TypeError: 'Classification' object is not subscriptable` error. Code:

```python
result = structured_llm.invoke("Classify this...")
return {"category": result["sentiment"]}  # ← Crash here
```

<details>
<summary>✅ Diagnosis & Fix</summary>

**Problem:** Pydantic objects use **dot notation**, not bracket notation.

**Fix:**
```python
return {"category": result.sentiment}  # ← Use dot notation
```

**Prevention:** Always remember that `with_structured_output()` returns a Pydantic model instance, not a dictionary.
</details>

---

## 🏛️ Architecture Decision Scenarios

---

### Scenario 9: LangGraph vs Simple Chain

**Problem:** Your team needs to build:
1. A single-prompt translator (English → French)
2. A multi-step document processor with quality checking and retry loops
3. A customer support bot with routing and escalation

For each, would you use LangGraph or a simple LangChain chain? Justify.

<details>
<summary>✅ Approach</summary>

1. **Single-prompt translator → Simple chain / direct API call**
   - No branching, no loops, no state → LangGraph is overkill
   - Just `llm.invoke([HumanMessage("Translate: ...")])` is sufficient

2. **Multi-step document processor → LangGraph**
   - Needs retry loops (conditional edge back to re-process)
   - Needs state tracking (which documents are done, quality scores)
   - Needs fault tolerance (resume from checkpoint if crash occurs)

3. **Customer support bot → LangGraph**
   - Needs conditional routing (classify intent → route to handler)
   - Needs conversation memory (checkpointer)
   - Needs human escalation (human-in-the-loop)
   - Needs multi-turn state management
</details>

---

### Scenario 10: Choosing the Right Checkpointer

**Problem:** Your team is deploying 3 different LangGraph apps:
1. A local development prototype
2. A single-server production chatbot (small startup)
3. A multi-server production system (500K users)

Which checkpointer would you recommend for each?

<details>
<summary>✅ Approach</summary>

1. **Local prototype → `MemorySaver`**
   - Fast, zero setup, no dependencies
   - Acceptable to lose state on restart during development

2. **Single-server production → `SqliteSaver`**
   - Persists to disk (survives restarts)
   - No external database needed
   - Good for small-to-medium load

3. **Multi-server production → `PostgresSaver`**
   - Shared across all servers (single source of truth)
   - Handles high concurrency
   - Supports backup, replication, monitoring
   - Can scale with the database
</details>

---

### Scenario 11: Designing State for a Complex Application

**Problem:** You're building a job application review system that:
- Parses a resume (extract skills, experience, education)
- Evaluates against job requirements (3 evaluators in parallel)
- Generates an overall score
- Routes to "shortlisted" or "rejected" based on score
- Optionally loops back for human review

Design the **State TypedDict**. What reducers are needed and why?

<details>
<summary>✅ Approach</summary>

```python
from typing import TypedDict, Annotated
import operator

class ApplicationState(TypedDict):
    # Input
    resume_text: str
    job_requirements: dict

    # Parsed resume
    skills: list[str]
    experience_years: int
    education: str

    # Parallel evaluations (NEEDS REDUCER)
    evaluations: Annotated[list[dict], operator.add]

    # Aggregated result
    overall_score: float
    decision: str            # "shortlisted" or "rejected"
    feedback: str

    # Human review
    human_reviewed: bool
    human_override: str      # Optional override of decision

    # Metadata
    attempts: int
```

**Why `operator.add` reducer?** Three parallel evaluators (skills match, experience match, education match) each write to `evaluations`. Without the reducer, only one evaluation would survive.

**Additional considerations:**
- `human_reviewed` enables conditional routing to human review
- `attempts` enables loop termination
- `human_override` allows `update_state()` for HITL
</details>

---

## 🔥 Production Scenarios

---

### Scenario 12: Handling a Production Outage

**Problem:** Your LangGraph chatbot in production (using `PostgresSaver`) crashes mid-conversation for a user. The crash happens after node 3 of 5 has completed. The user tries to send a new message. What happens? How does LangGraph handle this?

<details>
<summary>✅ Approach</summary>

**What happens automatically:**
1. Nodes 1, 2, and 3 have already been checkpointed to PostgreSQL
2. When the server restarts and the user sends a new message with the same `thread_id`...
3. LangGraph loads the last checkpoint (after node 3)
4. Execution resumes from node 4 — no work is lost!

**What you need to ensure:**
- **Idempotent nodes** — If node 3 partially executed before the crash, it will be re-run. Make sure nodes handle this correctly (e.g., don't double-charge a payment)
- **Error logging** — Log the crash details for investigation
- **Health checks** — Monitor server health and auto-restart
- **Graceful degradation** — Return a "please try again" message if recovery fails
</details>

---

### Scenario 13: Scaling for High Traffic

**Problem:** Your LangGraph application handles 100 requests/minute now, but you expect 10,000/minute after a product launch. How would you scale?

<details>
<summary>✅ Approach</summary>

**1. Horizontal scaling:**
- Deploy multiple server instances behind a load balancer
- Use `PostgresSaver` (shared database) so any server can handle any thread

**2. Async execution:**
```python
# Use async nodes and ainvoke for better concurrency
async def my_node(state):
    result = await llm.ainvoke(state["messages"])
    return {"messages": [result]}

result = await app.ainvoke(input, config)
```

**3. LangGraph Platform:**
- Use the managed platform for auto-scaling, task queues, and background runs

**4. Optimization:**
- Cache frequently retrieved documents
- Use faster/smaller models for classification (routing) nodes
- Implement request deduplication
- Use connection pooling for database checkpointers

**5. Monitoring (LangSmith):**
- Track latency per node to identify bottlenecks
- Monitor token usage to optimize costs
- Set up alerts for error rate spikes
</details>

---

### Scenario 14: Data Privacy and Compliance

**Problem:** Your company operates in the EU (GDPR). Your LangGraph chatbot stores conversation history. A user requests data deletion under GDPR's "right to be forgotten." How do you handle this?

<details>
<summary>✅ Approach</summary>

**Immediate actions:**
1. **Delete all checkpoints** for the user's `thread_id` from the database
2. **Delete any cached state** in MemorySaver instances
3. **Log the deletion** for compliance audit trail

**Design considerations for GDPR compliance:**
1. **Data mapping** — Know exactly where user data is stored (checkpointer DB, logs, LangSmith traces)
2. **Retention policies** — Implement TTL on checkpoints (auto-delete after 30 days)
3. **Encryption** — Encrypt state at rest in the checkpointer database
4. **Anonymization** — Don't store PII in state if possible; use user IDs instead of names
5. **Consent** — Get explicit consent before storing conversation history
6. **LangSmith** — Ensure traces don't contain PII, or configure PII scrubbing
</details>

---

### Scenario 15: Monitoring & Alerting Strategy

**Problem:** You deployed a LangGraph application and need to set up monitoring. What metrics would you track, what thresholds would you set, and how would you handle alerts?

<details>
<summary>✅ Approach</summary>

**Metrics to track:**

| Metric | Threshold | Alert Level |
|--------|-----------|-------------|
| End-to-end latency | > 10s | Warning |
| End-to-end latency | > 30s | Critical |
| Node error rate | > 5% | Warning |
| Node error rate | > 15% | Critical |
| LLM API error rate | > 10% | Critical |
| Loop iterations (avg) | > 3 | Warning |
| Checkpoint DB latency | > 500ms | Warning |
| Token usage per request | > 10K tokens | Warning |
| Active threads | > 10K | Info |
| Memory usage | > 80% | Warning |

**Implementation:**
- **LangSmith** for trace-level observability
- **Custom metrics** exported to Prometheus/Grafana
- **PagerDuty / Slack alerts** for critical thresholds
- **Dashboard** showing real-time health of all graph nodes
</details>

---

## 📊 Scenario Tracker

| # | Scenario | Category | Status |
|---|----------|----------|--------|
| 1 | Customer Support Chatbot | System Design | ☐ |
| 2 | Multi-Agent Research Assistant | System Design | ☐ |
| 3 | RAG with Hallucination Detection | System Design | ☐ |
| 4 | Order Processing Pipeline | System Design | ☐ |
| 5 | Silent State Bug | Debugging | ☐ |
| 6 | Infinite Loop | Debugging | ☐ |
| 7 | Memory Not Working | Debugging | ☐ |
| 8 | Pydantic Crash | Debugging | ☐ |
| 9 | LangGraph vs Simple Chain | Architecture | ☐ |
| 10 | Choosing Checkpointers | Architecture | ☐ |
| 11 | Complex State Design | Architecture | ☐ |
| 12 | Production Outage Recovery | Production | ☐ |
| 13 | Scaling for High Traffic | Production | ☐ |
| 14 | GDPR Data Privacy | Production | ☐ |
| 15 | Monitoring & Alerting | Production | ☐ |

---

> ⬅️ [Back to Main Guide](./README.md) | ⬅️ [Previous: Coding Exercises](./03_Coding_Exercises.md) | ➡️ [Next: Cheat Sheet](./05_Cheat_Sheet.md)
