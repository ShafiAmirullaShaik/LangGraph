# ============================================================
# Iterative Workflow — Simple Counter (Loop Example)
# ============================================================
# This is the SIMPLEST possible iterative (looping) workflow.
#
# What is an Iterative Workflow?
#   - A workflow where a node can go BACK to a previous node
#     instead of always going forward.
#   - It keeps looping until a condition is met.
#   - Uses `add_conditional_edges()` to decide:
#     → Should we LOOP again? or STOP?
#
# What this does:
#   - Starts a counter at 0.
#   - Each loop adds 1 to the counter.
#   - When the counter reaches the target, it stops.
#
# Flow:
#   START → add_one → check_count →
#       (if count < target) → loop back to add_one   🔁
#       (if count >= target) → done → END             ✅
# ============================================================

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# --- State: holds the counter and target ---
class CounterState(TypedDict):
    count: int       # current count
    target: int      # stop when count reaches this


# --- Node 1: Add one to the counter ---
def add_one(state: CounterState):
    new_count = state['count'] + 1
    print(f"🔄 Count: {new_count}")
    return {"count": new_count}


# --- Node 2: Show the final result ---
def done(state: CounterState):
    print(f"\n✅ Done! Final count: {state['count']}")
    return {}


# --- Routing Function: Loop or Stop? ---
def check_count(state: CounterState):
    """
    This is the KEY part of an iterative workflow.
    It decides: should we go back to 'add_one' (loop)
    or go to 'done' (stop)?
    """
    if state['count'] < state['target']:
        return "add_one"     # 🔁 loop back
    else:
        return "done"        # ✅ stop


# --- Build the Graph ---
graph = StateGraph(CounterState)

# Add nodes
graph.add_node("add_one", add_one)
graph.add_node("done", done)

# START goes to add_one
graph.add_edge(START, "add_one")

# After add_one, check if we should loop or stop
graph.add_conditional_edges(
    "add_one",          # after this node...
    check_count,        # run this function to decide...
    ["add_one", "done"] # possible next nodes
)

# done goes to END
graph.add_edge("done", END)

# Compile
app = graph.compile()


# --- Run it! ---
target = int(input("🎯 Enter a target number to count to: "))

print("=" * 30)
print(f"🎯 Counting to {target}")
print("=" * 30)

result = app.invoke({"count": 0, "target": target})

print(f"\n📊 Final State: {result}")
