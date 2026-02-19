import os
from pathlib import Path
from langgraph.graph import StateGraph, START, END
from typing import List, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import sqlite3

# Load .env from the LangGraph root directory
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.2, api_key=GROQ_API_KEY)

class ChatBot(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    
    
def chat_node(state: ChatBot) -> ChatBot:
    messages = state["messages"]
    
    response = llm.invoke(messages)
    
    return {
        "messages": [response]
    }

# Create SQLite database and table
conn = sqlite3.connect("chatbot.db", check_same_thread=False)

checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatBot)

graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

app = graph.compile(checkpointer=checkpointer)

def get_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)