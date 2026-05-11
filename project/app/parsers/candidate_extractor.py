import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.candidate import Candidate
from app.utils.config import settings

def extract_candidate_from_text(raw_text: str, source: str) -> Candidate:
    """
    Extracts structured candidate profile from raw resume text using Gemini.
    """
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set.")
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.0
    )
    
    structured_llm = llm.with_structured_output(Candidate)
    
    prompt = f"""
    You are an expert HR assistant. Extract the candidate's profile from the following resume text.
    If a field is missing, leave it empty or default.
    Always generate a unique ID if one is not provided.
    
    Resume Text:
    {raw_text}
    """
    
    candidate = structured_llm.invoke(prompt)
    candidate.resume_source = source
    candidate.raw_text = raw_text
    
    if not candidate.id:
        candidate.id = str(uuid.uuid4())
        
    return candidate
