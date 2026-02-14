from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from typing import TypedDict, Annotated
import os
import dotenv

dotenv.load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

class LLMState(TypedDict):
    query: str
    response: str

def llm_query(state: LLMState) -> LLMState:
    print(f'Query: {state["query"]}')
    print(f'Processing...')
    response = llm.invoke([SystemMessage(content="You are a helpful assistant."), HumanMessage(content=state["query"])])
    state["response"] = response.content
    print(f'Response: {state["response"]}')
    return state

graph = StateGraph(LLMState)
graph.add_node("llm_query", llm_query)
graph.add_edge(START, "llm_query")
graph.add_edge("llm_query", END)

app = graph.compile()

response = app.invoke({"query": "What is the capital of France?"})