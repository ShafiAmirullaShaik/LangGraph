# ============================================================
# Conditional Workflow — Voter Eligibility Checker
# ============================================================
# This workflow checks whether a citizen is eligible to vote
# in an election based on multiple criteria:
#   1. Age (must be 18 or above)
#   2. Citizenship (must be a citizen of India)
#   3. Criminal record (must have no criminal record)
#
# Flow:
#   START → collect_info → verify_age →
#       (if age < 18)         → reject_underage → END
#       (if age >= 18)        → verify_citizenship →
#           (if not citizen)  → reject_non_citizen → END
#           (if citizen)      → verify_criminal_record →
#               (if criminal) → reject_criminal → END
#               (if clean)    → approve_voter → END
# ============================================================

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.2, api_key=os.getenv("GROQ_API_KEY"))


# --- State Definition ---
class VoterState(TypedDict):
    name: str
    age: int
    is_citizen: bool
    has_criminal_record: bool
    status: str          # "pending", "approved", "rejected"
    reason: str          # Reason for approval or rejection
    voter_id: str        # Voter ID (assigned if approved)


# ============================================================
# NODE FUNCTIONS
# ============================================================

def collect_info(state: VoterState):
    """
    Node 1: Collect and display the voter's information.
    This is the entry point of the workflow.
    """
    print("=" * 50)
    print("📋 VOTER ELIGIBILITY CHECK")
    print("=" * 50)
    print(f"  Name             : {state['name']}")
    print(f"  Age              : {state['age']}")
    print(f"  Indian Citizen   : {'Yes' if state['is_citizen'] else 'No'}")
    print(f"  Criminal Record  : {'Yes' if state['has_criminal_record'] else 'No'}")
    print("=" * 50)
    return {"status": "pending"}


def verify_age(state: VoterState):
    """
    Node 2: Verify if the voter meets the minimum age requirement.
    In India, the minimum voting age is 18 years.
    """
    print(f"\n🔍 Step 1: Verifying age... (Age: {state['age']})")
    return {}


def reject_underage(state: VoterState):
    """
    Rejection Node: Voter is below 18 years of age.
    """
    years_left = 18 - state['age']
    print(f"❌ REJECTED: {state['name']} is only {state['age']} years old.")
    print(f"   Must wait {years_left} more year(s) to be eligible.")
    return {
        "status": "rejected",
        "reason": f"Underage — must be at least 18 years old. Currently {state['age']}, need to wait {years_left} more year(s).",
        "voter_id": "N/A"
    }


def verify_citizenship(state: VoterState):
    """
    Node 3: Verify if the voter is a citizen of India.
    Only Indian citizens are eligible to vote in Indian elections.
    """
    print(f"✅ Age verified: {state['age']} years old (meets minimum age of 18)")
    print(f"\n🔍 Step 2: Verifying citizenship...")
    return {}


def reject_non_citizen(state: VoterState):
    """
    Rejection Node: Voter is not an Indian citizen.
    """
    print(f"❌ REJECTED: {state['name']} is not an Indian citizen.")
    return {
        "status": "rejected",
        "reason": "Not an Indian citizen — only Indian citizens can vote in Indian elections.",
        "voter_id": "N/A"
    }


def verify_criminal_record(state: VoterState):
    """
    Node 4: Verify if the voter has any criminal record.
    Voters with criminal convictions may be disqualified.
    """
    print(f"✅ Citizenship verified: Indian citizen")
    print(f"\n🔍 Step 3: Checking criminal record...")
    return {}


def reject_criminal(state: VoterState):
    """
    Rejection Node: Voter has a criminal record.
    """
    print(f"❌ REJECTED: {state['name']} has a criminal record.")
    return {
        "status": "rejected",
        "reason": "Has a criminal record — voters with criminal convictions are disqualified.",
        "voter_id": "N/A"
    }


def approve_voter(state: VoterState):
    """
    Approval Node: Voter has passed all checks.
    A voter ID is generated and the voter is approved.
    """
    voter_id = f"VOTE-2026-{abs(hash(state['name'])) % 100000:05d}"
    print(f"✅ No criminal record found")
    print(f"\n🎉 APPROVED! {state['name']} is eligible to vote!")
    print(f"   Voter ID: {voter_id}")
    return {
        "status": "approved",
        "reason": "All eligibility criteria met — age, citizenship, and clean record verified.",
        "voter_id": voter_id
    }


# ============================================================
# CONDITIONAL ROUTING FUNCTIONS
# ============================================================

def check_age(state: VoterState):
    """
    Conditional Edge: Routes based on the voter's age.
    - If age >= 18 → proceed to verify_citizenship
    - If age < 18  → go to reject_underage
    """
    if state['age'] >= 18:
        return "verify_citizenship"
    else:
        return "reject_underage"


def check_citizenship(state: VoterState):
    """
    Conditional Edge: Routes based on citizenship status.
    - If citizen     → proceed to verify_criminal_record
    - If not citizen → go to reject_non_citizen
    """
    if state['is_citizen']:
        return "verify_criminal_record"
    else:
        return "reject_non_citizen"


def check_criminal_record(state: VoterState):
    """
    Conditional Edge: Routes based on criminal record.
    - If no criminal record → approve_voter
    - If has criminal record → reject_criminal
    """
    if not state['has_criminal_record']:
        return "approve_voter"
    else:
        return "reject_criminal"


# ============================================================
# BUILD THE GRAPH
# ============================================================

graph = StateGraph(VoterState)

# Add all nodes
graph.add_node("collect_info", collect_info)
graph.add_node("verify_age", verify_age)
graph.add_node("reject_underage", reject_underage)
graph.add_node("verify_citizenship", verify_citizenship)
graph.add_node("reject_non_citizen", reject_non_citizen)
graph.add_node("verify_criminal_record", verify_criminal_record)
graph.add_node("reject_criminal", reject_criminal)
graph.add_node("approve_voter", approve_voter)

# Sequential edges (fixed flow)
graph.add_edge(START, "collect_info")
graph.add_edge("collect_info", "verify_age")

# Conditional edge 1: After age check → citizenship or reject
graph.add_conditional_edges(
    "verify_age",
    check_age,
    ["verify_citizenship", "reject_underage"]
)

# Conditional edge 2: After citizenship check → criminal record or reject
graph.add_conditional_edges(
    "verify_citizenship",
    check_citizenship,
    ["verify_criminal_record", "reject_non_citizen"]
)

# Conditional edge 3: After criminal record check → approve or reject
graph.add_conditional_edges(
    "verify_criminal_record",
    check_criminal_record,
    ["approve_voter", "reject_criminal"]
)

# All terminal nodes lead to END
graph.add_edge("reject_underage", END)
graph.add_edge("reject_non_citizen", END)
graph.add_edge("reject_criminal", END)
graph.add_edge("approve_voter", END)


# ============================================================
# COMPILE AND RUN
# ============================================================

app = graph.compile()


result1 = app.invoke({
    "name": "Shafi Amirulla",
    "age": 25,
    "is_citizen": True,
    "has_criminal_record": False
})
print(f"\n📄 Final Result: {result1['status'].upper()} — {result1['reason']}")
