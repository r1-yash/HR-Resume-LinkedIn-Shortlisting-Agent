import os
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.jd import JobDescription
from app.utils.config import settings

def parse_jd(raw_text: str) -> JobDescription:
    """
    Parses raw Job Description text into a structured Pydantic model using Gemini.
    """
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set.")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.0
    )
    
    structured_llm = llm.with_structured_output(JobDescription)
    
    prompt = f"""
    You are an expert HR assistant. Your task is to extract structured information from the following Job Description.
    
    Job Description:
    {raw_text}
    """
    
    result = structured_llm.invoke(prompt)
    return result
