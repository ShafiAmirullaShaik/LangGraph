from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from typing import TypedDict, Annotated, List
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
import os
import operator
import dotenv

dotenv.load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

essay = """
Artificial Intelligence (AI) in India plays a transformative role across multiple sectors, driving innovation, efficiency, and inclusive growth. In healthcare, AI enables early disease detection, telemedicine, and affordable diagnostics, while in agriculture it supports farmers with crop monitoring, soil analysis, and weather forecasting. Education benefits from AI-powered personalized learning and language translation tools that bridge rural gaps, and governance uses AI for digital services, fraud detection, and policy-making. Industries such as manufacturing, finance, and IT leverage AI for automation, risk management, and global competitiveness, contributing significantly to India’s GDP. However, challenges like job displacement, ethical concerns, lack of infrastructure, and skill shortages remain. To address these, the government has launched initiatives such as the National AI Strategy and the India AI Mission, focusing on safe, trusted, and inclusive AI development. Overall, AI is not just a technological advancement but a socio-economic enabler, positioning India to achieve its vision of “AI for All” and emerge as a global leader in innovation.
"""

class ResponseState(BaseModel):
    feedback: str = Field(description="Detailed feedback for the essay")
    score: int = Field(description="Score out of 10", ge=0, le=10)

structured_llm = llm.with_structured_output(schema=ResponseState)

class UPSEState(TypedDict):
    essay: str
    language_feedback: str
    analysis_feedback: str
    clarity_feedback: str
    individual_scores: Annotated[List[int], operator.add]
    overall_feedback: str
    overall_score: float


def evaluate_language(state: UPSEState) -> UPSEState:
    print(f'Generating language feedback...')
    prompt = [
        SystemMessage(content="You are a language expert and you will evaluate the language quality of the following essay and provide a feedback and score out of 10."),
        HumanMessage(content=f"Essay: {state['essay']}")
    ]
    
    response = structured_llm.invoke(prompt)
    
    return {'language_feedback': response.feedback, 'individual_scores': [response.score]}

def evaluate_analysis(state: UPSEState) -> UPSEState:
    print(f'Generating analysis feedback...')
    prompt = [
        SystemMessage(content="You are an analysis expert and you will evaluate the analysis quality of the following essay and provide a feedback and score out of 10."),
        HumanMessage(content=f"Essay: {state['essay']}")
    ]
    
    response = structured_llm.invoke(prompt)
    
    return {'analysis_feedback': response.feedback, 'individual_scores': [response.score]}

def evaluate_thought(state: UPSEState) -> UPSEState:
    print(f'Generating clarity of thought feedback...')
    prompt = [
        SystemMessage(content="You are a clarity of thought expert and you will evaluate the clarity of thought quality of the following essay and provide a feedback and score out of 10."),
        HumanMessage(content=f"Essay: {state['essay']}")
    ]
    
    response = structured_llm.invoke(prompt)
    
    return {'clarity_feedback': response.feedback, 'individual_scores': [response.score]}

def final_evaluation(state: UPSEState) -> UPSEState:
    print(f'Generating final evaluation...')
    prompt = [
        SystemMessage(content="You are a final evaluation expert and Based on the following feedback, provide an overall feedback."),
        HumanMessage(content=f"Language Feedback: {state['language_feedback']}\nAnalysis Feedback: {state['analysis_feedback']}\nClarity of Thought Feedback: {state['clarity_feedback']}")
    ]
    
    response = llm.invoke(prompt)

    # Calculate overall score
    overall_score = sum(state['individual_scores']) / len(state['individual_scores'])
    
    return {'overall_feedback': response.content, 'overall_score': overall_score}

graph = StateGraph(UPSEState)

graph.add_node('evaluate_language', evaluate_language)
graph.add_node('evaluate_analysis', evaluate_analysis)
graph.add_node('evaluate_thought', evaluate_thought)
graph.add_node('final_evaluation', final_evaluation)

graph.add_edge(START, 'evaluate_language')
graph.add_edge(START, 'evaluate_analysis')
graph.add_edge(START, 'evaluate_thought')

graph.add_edge('evaluate_language', 'final_evaluation')
graph.add_edge('evaluate_analysis', 'final_evaluation')
graph.add_edge('evaluate_thought', 'final_evaluation')

graph.add_edge('final_evaluation', END)

app = graph.compile()

response = app.invoke({
    'essay': essay
})

print("Overall Feedback: ", response['overall_feedback'])
print("Overall Score: ", response['overall_score'])










    

