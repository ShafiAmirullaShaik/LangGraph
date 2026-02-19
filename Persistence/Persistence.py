# Persistence in LangGraph refers to the ability to save and restore the state of a workflow over time.
# This is useful for long-running workflows or workflows that need to be resumed after a failure.
# LangGraph provides a simple API for persistence, which is built on top of LangChain's persistence module.
# Fault tolerance: The ability of a system to continue operating properly in the event of the failure of some of its components.
# Example: If a node fails, the workflow can be resumed from the last checkpoint. 

# Checkpointer: A mechanism that captures and stores the state of the graph at each step.
# - It enables state recovery, allowing a workflow to resume from a specific checkpoint after a failure.
# - It supports multi-turn conversations by persisting state across different interactions using a unique `thread_id`.
# Example: `MemorySaver` is an in-memory checkpointer that saves snapshots of the `State` after every node execution.

# Threads: Unique identifiers used to isolate and manage separate state instances within the same graph.
# - A `thread_id` allows the checkpointer to store and retrieve state for a specific session or user.
# - This ensures that multiple concurrent conversations remain independent and isolated from each other.
# - By providing the same `thread_id`, a workflow can be resumed exactly where it left off in a previous interaction.

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated, List
from langgraph.checkpoint.memory import MemorySaver, InMemorySaver
import os
import dotenv
import json
import operator

dotenv.load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

class JokeState(TypedDict):
    topic: str
    joke: str
    explaination: str

def generate_joke(state: JokeState):
    topic = state["topic"]
    response = llm.invoke(f"Tell me a joke on {topic}.")
    return {"joke": response.content}

def generate_explanation(state: JokeState):
    joke = state["joke"]
    return {"explaination": llm.invoke(f"Explain the joke {joke}").content}

graph = StateGraph(JokeState)
graph.add_node("generate_joke", generate_joke)
graph.add_node("generate_explanation", generate_explanation)

graph.add_edge(START, "generate_joke")
graph.add_edge("generate_joke", "generate_explanation")
graph.add_edge("generate_explanation", END)

checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)

thread_id = '1'
config = {
    "configurable": {
        "thread_id": thread_id
    }
}

thread_id_1 = '2'
config1 = {
    "configurable": {
        "thread_id": thread_id_1
    }
}

response = app.invoke({"topic": "AI"}, config = config1)
print(response)
print('\n')
print(app.get_state(config))
print('\n')
print(list(app.get_state_history(config)))


