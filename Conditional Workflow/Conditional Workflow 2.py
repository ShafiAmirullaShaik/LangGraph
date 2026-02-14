from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.2, api_key=os.getenv("GROQ_API_KEY"))

class SentimentSchema(BaseModel):
    sentiment: Literal['positive', 'negative', 'neutral'] = Field(description="Sentiment of the report")

structred_llm = llm.with_structured_output(schema=SentimentSchema)

report = '''
Patient: Rajesh Kumar, Male, Age 45. Presented with persistent chest pain, shortness of breath, and elevated blood pressure (160/100 mmHg). ECG reveals mild ST-segment depression; blood tests show elevated LDL cholesterol (210 mg/dL) and blood sugar (180 mg/dL). 
Diagnosis: Hypertensive heart disease with hyperlipidemia and pre-diabetic condition. 
Recommended: Immediate lifestyle modification, medication for BP and cholesterol, and follow-up cardiac evaluation in 2 weeks.
'''

class ReviewState(TypedDict):
    review: str
    sentiment: Literal['positive', 'negative', 'neutral']
    diagnosis: dict
    response: str

class DiagnosisSchema(BaseModel):
    issue_type: Literal['acute', 'chronic', 'acute_chronic', 'other'] = Field(description="Type of issue")
    tone: Literal['angry', 'happy', 'sad', 'neutral'] = Field(description="Emotion of the report")
    urgency: Literal['low', 'medium', 'high'] = Field(description="Urgency of the report")

diagnosis_structred_llm = llm.with_structured_output(schema=DiagnosisSchema)

def find_sentiment(state: ReviewState):
    response = structred_llm.invoke([
    SystemMessage(content="You are a expert in medical field and you have to classify the sentiment of the following report"), 
    HumanMessage(content=f"Classify the sentiment of the following report: {state['review']}")])
    
    return {"sentiment": response.sentiment}

def check_sentiment(state: ReviewState):
    if state['sentiment'] == 'positive':
        return "positive_report"
    elif state['sentiment'] == 'negative':
        return "run_diagnosis"
    else:
        return "neutral_report"

def positive_report(state: ReviewState):
    prompt = f'''
        write a warm thank you message in response to this report:
        \n\n
        {state['review']}. Give healthy lifestyle recommendations in a simple and easy to understand way.
    '''

    response = llm.invoke(prompt)

    return {"response": response.content}


def run_diagnosis(state: ReviewState):
    prompt = f'''
        write a diagnosis for this report:
        \n\n
        {state['review']}
        Return the issue_type, tone and urgency.
    '''
    response = diagnosis_structred_llm.invoke(prompt)

    return {"diagnosis": response.model_dump()}

def neutral_report(state: ReviewState):
    prompt = f'''
        write a neutral message in response to this report:
        \n\n
        {state['review']}
    '''
    response = llm.invoke(prompt)

    return {"response": response.content}

def negative_report(state: ReviewState):
    prompt = f'''
        write a negative message in response to this report. Suggest medications and lifestyle changes.
        \n\n
        {state['review']}
        the user had a {state['diagnosis']['issue_type']} issue.
        the user is feeling {state['diagnosis']['tone']}.
        the user is {state['diagnosis']['urgency']}.

        Write an empathetic message to the user.
    '''
    response = llm.invoke(prompt)

    return {"response": response.content}

graph = StateGraph(ReviewState)
graph.add_node("find_sentiment", find_sentiment)
graph.add_node("positive_report", positive_report)
graph.add_node("run_diagnosis", run_diagnosis)
graph.add_node("neutral_report", neutral_report)
graph.add_node("negative_report", negative_report)

graph.add_edge(START, "find_sentiment")

graph.add_conditional_edges("find_sentiment", check_sentiment, {
    'positive_report': 'positive_report',
    'run_diagnosis': 'run_diagnosis',
    'neutral_report': 'neutral_report'
})

graph.add_edge("positive_report", END)
graph.add_edge("run_diagnosis", "negative_report")
graph.add_edge("negative_report", END)
graph.add_edge("neutral_report", END)

app = graph.compile()

response = app.invoke({"review": report})
print(response['response'])
print(response['diagnosis'])

