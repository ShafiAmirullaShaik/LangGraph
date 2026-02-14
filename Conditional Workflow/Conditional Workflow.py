from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.2, api_key=os.getenv("GROQ_API_KEY"))

class QState(TypedDict):
    a: int
    b: int
    c: int
    equation: str
    d: float
    result: str

def show_equation(state: QState):
    equation = f"{state['a']}x^2 + {state['b']}x + {state['c']}"
    return {"equation": equation}

def calculate_d(state: QState):
    d = state['b']**2 - 4*state['a']*state['c']
    return {"d": d}

def real_roots(state: QState):
    x1 = (-state['b'] + state['d']**0.5) / (2*state['a'])
    x2 = (-state['b'] - state['d']**0.5) / (2*state['a'])
    return {"result": f"The roots are {x1} and {x2}"}

def repeated_roots(state: QState):
    x = -state['b'] / (2*state['a'])
    return {"result": f"The root is {x}"}

def no_real_roots(state: QState):
    return {"result": "The roots are not real"}

def check_d(state: QState):
    if state['d'] > 0:
        return "real_roots"
    elif state['d'] == 0:
        return "repeated_roots"
    else:
        return "no_real_roots"

graph = StateGraph(QState)
graph.add_node("show_equation", show_equation)
graph.add_node("calculate_d", calculate_d)
graph.add_node("real_roots", real_roots)
graph.add_node("repeated_roots", repeated_roots)
graph.add_node("no_real_roots", no_real_roots)

graph.add_edge(START, "show_equation")
graph.add_edge("show_equation", "calculate_d")

graph.add_conditional_edges(
    "calculate_d", 
    check_d, 
    ["real_roots", "repeated_roots", "no_real_roots"]
)

graph.add_edge("real_roots", END)
graph.add_edge("repeated_roots", END)
graph.add_edge("no_real_roots", END)

app = graph.compile()

response = app.invoke({"a": 2, "b": 4, "c": 8})
print(response)

