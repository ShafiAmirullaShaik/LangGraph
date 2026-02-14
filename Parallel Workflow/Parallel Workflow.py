from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from typing import TypedDict, Annotated
import os
import dotenv

dotenv.load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

class PlayerState(TypedDict):
    runs: int
    balls: int
    fours: int
    sixes: int
    sr: float
    bpb: float
    bp: float
    summary: str

def strike_rate(state: PlayerState) -> dict:
    print(f'Calculating strike rate...')
    sr = (state['runs'] / state['balls']) * 100
    return {'sr': sr}

def balls_per_boundary(state: PlayerState) -> dict:
    print(f'Calculating balls per boundary...')
    bpb = state['balls'] / (state['fours'] + state['sixes'])
    return {'bpb': bpb}

def boundary_percentage(state: PlayerState) -> dict:
    print(f'Calculating boundary percentage...')
    bp = ((state['fours'] + state['sixes']) / state['runs']) * 100
    return {'bp': bp}

def player_summary(state: PlayerState) -> dict:
    print(f'Generating player summary...')
    summary = f'''Player Summary:
    Runs: {state['runs']}
    Balls: {state['balls']}
    Fours: {state['fours']}
    Sixes: {state['sixes']}
    Strike Rate: {state['sr']}
    Balls per Boundary: {state['bpb']}
    Boundary Percentage: {state['bp']}
    '''
    return {'summary': summary}

graph = StateGraph(PlayerState)

graph.add_node('strike_rate', strike_rate)
graph.add_node('balls_per_boundary', balls_per_boundary)
graph.add_node('boundary_percentage', boundary_percentage)
graph.add_node('player_summary', player_summary)

graph.add_edge(START, 'strike_rate')
graph.add_edge(START, 'balls_per_boundary')
graph.add_edge(START, 'boundary_percentage')

graph.add_edge('strike_rate', 'player_summary')
graph.add_edge('balls_per_boundary', 'player_summary')
graph.add_edge('boundary_percentage', 'player_summary')

graph.add_edge('player_summary', END)

app = graph.compile()

response = app.invoke({
    'runs': 100,
    'balls': 40,
    'fours': 10,
    'sixes': 10,
})

print(response)







    

