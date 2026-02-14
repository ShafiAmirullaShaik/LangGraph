from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from typing import TypedDict, Annotated
import os
import dotenv

dotenv.load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

class BMIState(TypedDict):
    weight: float
    height: float
    bmi: float
    category: str

def calculate_bmi(state: BMIState) -> BMIState:
    '''
    This function calculates the BMI based on the weight and height provided in the state.
    '''
    print(f'Processing...')
    print(f'Weight: {state["weight"]}')
    print(f'Height: {state["height"]}')
    print(f'Calculating BMI...')
    state["bmi"] = state["weight"] / (state["height"] ** 2)
    print(f'BMI: {state["bmi"]}')

    return state

def label_bmi(state: BMIState) -> BMIState:
    '''
    This function labels the BMI based on the BMI value.
    '''
    print(f'Labeling BMI...')
    if state["bmi"] < 18.5:
        state["category"] = "Underweight"
    elif state["bmi"] < 25:
        state["category"] = "Normal weight"
    elif state["bmi"] < 30:
        state["category"] = "Overweight"
    else:
        state["category"] = "Obesity"
        
    print(f'Category: {state["category"]}')

    return state

graph = StateGraph(BMIState)

graph.add_node("calculate_bmi", calculate_bmi)
graph.add_node("label_bmi", label_bmi)

graph.add_edge(START, "calculate_bmi")
graph.add_edge("calculate_bmi", "label_bmi")
graph.add_edge("label_bmi", END)

app = graph.compile()

response = app.invoke({"weight": 70, "height": 1.75})

print(response)


