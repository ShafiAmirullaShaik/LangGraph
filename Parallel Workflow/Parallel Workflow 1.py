from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from typing import TypedDict, Annotated
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field
import os
import dotenv

dotenv.load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))

class UPSEState(BaseModel):
    feedback: str = Field(description="Detailed feedback for the essay")
    score: int = Field(description="Score out of 10", ge=0, le=10)

structured_llm = llm.with_structured_output(schema=UPSEState)

essay = """
Artificial Intelligence (AI) in India plays a transformative role across multiple sectors, driving innovation, efficiency, and inclusive growth. In healthcare, AI enables early disease detection, telemedicine, and affordable diagnostics, while in agriculture it supports farmers with crop monitoring, soil analysis, and weather forecasting. Education benefits from AI-powered personalized learning and language translation tools that bridge rural gaps, and governance uses AI for digital services, fraud detection, and policy-making. Industries such as manufacturing, finance, and IT leverage AI for automation, risk management, and global competitiveness, contributing significantly to India’s GDP. However, challenges like job displacement, ethical concerns, lack of infrastructure, and skill shortages remain. To address these, the government has launched initiatives such as the National AI Strategy and the India AI Mission, focusing on safe, trusted, and inclusive AI development. Overall, AI is not just a technological advancement but a socio-economic enabler, positioning India to achieve its vision of “AI for All” and emerge as a global leader in innovation.
"""

prompt = f"""
Evaluate the following essay:
{essay}

Provide feedback and a score (out of 10) based on the following criteria:
1. Content: The essay should be well-structured, with clear arguments and examples.
2. Clarity: The essay should be easy to understand and free of grammatical errors.
3. Originality: The essay should be original and not plagiarized.
4. Length: The essay should be at least 500 words.
5. Spelling: The essay should be free of spelling errors.
6. Grammar: The essay should be free of grammatical errors.
7. Punctuation: The essay should be free of punctuation errors.
8. Style: The essay should be written in a clear and concise style.
9. Organization: The essay should be organized in a logical and coherent manner.
10. Coherence: The essay should be coherent and easy to follow.
"""

response = structured_llm.invoke(prompt)

print(response.model_dump_json(indent=2))







    

