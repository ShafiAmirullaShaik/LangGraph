import os
from langgraph.graph import StateGraph, START, END
from typing import List, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

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

checkpointer = MemorySaver()
graph = StateGraph(ChatBot)

graph.add_node('chat_node', chat_node)

graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

app = graph.compile(checkpointer=checkpointer)

thread_id = '1'

while True:
    user_input = input("You: ")
    
    print("You entered:", user_input)
    print("Processing...")
    print("Bot is typing...")
    
    if user_input.strip().lower() in ['exit', 'quit', 'bye']:
        print("Exiting chat. Goodbye!")
        break
    
    config = {
        'configurable': {
            'thread_id': thread_id
        }
    }
    
    result = app.invoke({
        "messages": [HumanMessage(content=user_input)]
    }, config=config)
    
    print("Bot:", result['messages'][-1].content)
    print("-" * 50)
    print(app.get_state(config=config))




    

    
    
