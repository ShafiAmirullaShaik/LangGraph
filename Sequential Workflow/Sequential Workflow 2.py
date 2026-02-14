from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from typing import TypedDict, Annotated
import os
import dotenv

dotenv.load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

# ============================================================
# Prompt Chaining Workflow
# ============================================================
# A complex task (writing a blog post) is broken into 3 simpler
# prompts, where each prompt uses the previous prompt's output
# as input:
#   1. Generate Outline  →  2. Write Draft  →  3. Polish & Summarize
# ============================================================

# --- State Definition ---
class BlogState(TypedDict):
    topic: str        # User-provided topic
    outline: str      # Step 1 output: generated outline
    draft: str        # Step 2 output: full draft based on outline
    final_post: str   # Step 3 output: polished & summarized version


# --- Node 1: Generate Outline ---
def generate_outline(state: BlogState) -> BlogState:
    '''
    Takes the topic and generates a structured outline.
    '''
    print("=" * 50)
    print("Step 1: Generating Outline...")
    print(f'Topic: {state["topic"]}')
    print("=" * 50)

    response = llm.invoke([
        SystemMessage(content="You are an expert content strategist. Generate a clear, structured outline for a blog post."),
        HumanMessage(content=f'Create a detailed outline for a blog post on: {state["topic"]}')
    ])

    state["outline"] = response.content
    print(f'\nOutline:\n{state["outline"]}\n')
    return state


# --- Node 2: Write Draft ---
def write_draft(state: BlogState) -> BlogState:
    '''
    Takes the outline from Step 1 and writes a full draft.
    '''
    print("=" * 50)
    print("Step 2: Writing Draft from Outline...")
    print("=" * 50)

    response = llm.invoke([
        SystemMessage(content="You are a skilled blog writer. Write a compelling blog post based on the given outline. Keep it concise (around 300 words)."),
        HumanMessage(content=f'Write a blog post based on this outline:\n\n{state["outline"]}')
    ])

    state["draft"] = response.content
    print(f'\nDraft:\n{state["draft"]}\n')
    return state


# --- Node 3: Polish & Summarize ---
def polish_and_summarize(state: BlogState) -> BlogState:
    '''
    Takes the draft from Step 2, polishes it, and adds a summary.
    '''
    print("=" * 50)
    print("Step 3: Polishing & Summarizing...")
    print("=" * 50)

    response = llm.invoke([
        SystemMessage(content="You are a professional editor. Polish the given blog draft for clarity, grammar, and flow. Then add a 2-3 sentence summary at the end."),
        HumanMessage(content=f'Polish and summarize this blog draft:\n\n{state["draft"]}')
    ])

    state["final_post"] = response.content
    return state


# --- Build the Graph ---
graph = StateGraph(BlogState)

# Add nodes
graph.add_node("generate_outline", generate_outline)
graph.add_node("write_draft", write_draft)
graph.add_node("polish_and_summarize", polish_and_summarize)

# Chain the edges: START → outline → draft → polish → END
graph.add_edge(START, "generate_outline")
graph.add_edge("generate_outline", "write_draft")
graph.add_edge("write_draft", "polish_and_summarize")
graph.add_edge("polish_and_summarize", END)

# Compile the graph
app = graph.compile()

# --- Run the Prompt Chain ---
result = app.invoke({"topic": "Why Epstein files are very scary?"})

print("\n" + "=" * 50)
print("FINAL RESULT")
print("=" * 50)
print(result['final_post'])