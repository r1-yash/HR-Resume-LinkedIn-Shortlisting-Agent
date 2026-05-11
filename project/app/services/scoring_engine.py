from typing import Dict, Any
from app.models.candidate import Candidate
from app.models.jd import JobDescription
from app.services.semantic_matcher import match_skills, compute_similarity
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from app.utils.config import settings

class LLMScoreReasoning(BaseModel):
    experience_score: int = Field(ge=0, le=10, description="Score 0-10 for experience relevance")
    experience_justification: str = Field(description="One-line justification")
    education_score: int = Field(ge=0, le=10, description="Score 0-10 for education and certs")
    education_justification: str = Field(description="One-line justification")
    project_score: int = Field(ge=0, le=10, description="Score 0-10 for project/portfolio")
    project_justification: str = Field(description="One-line justification")
    communication_score: int = Field(ge=0, le=10, description="Score 0-10 for communication quality")
    communication_justification: str = Field(description="One-line justification")

def get_llm_reasoning(jd: JobDescription, candidate: Candidate) -> LLMScoreReasoning:
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not set.")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.0
    )
    
    structured_llm = llm.with_structured_output(LLMScoreReasoning)
    
    prompt = f"""
    You are an expert HR shortlisting agent. Compare the Candidate's profile to the Job Description.
    Provide a score (0 to 10) and a concise one-line justification for each of the following dimensions:
    
    1. Experience Relevance:
       - If the candidate has no meaningful professional or internship experience tied to the role (no roles, or only placeholders / empty experience), set experience_score to 0.
       - If they have experience but it is largely misaligned with the JD (wrong domain, unrelated roles, or minimal overlap with required responsibilities), score in the 3–5 range, targeting ~4 unless overlap is slightly better or worse.
       - Reserve higher scores (6–10) for clearly relevant, JD-aligned experience.
    2. Education & Certifications: CRITICAL RULE: ONLY evaluate if the candidate's degree name matches the JD requirement. DO NOT penalize them based on graduation year (e.g., if they graduate in 2027, score them highly as having the degree).
    3. Project / Portfolio: Judge both (a) relevance to the JD and (b) depth / sophistication. Classify projects mentally as too basic (tutorials, trivial demos, course homework with no depth), moderate (some real scope or stack fit), or strong (non-trivial complexity, production-minded or advanced technical work aligned with the role). Let that judgment drive the score: basic work scores low; strong, complex, well-aligned work scores high. Mention basic vs strong in the justification when applicable.
    4. Communication Quality: CRITICAL RULE: Evaluate this purely based on whether the resume has a clean structure, sufficient detailed wording, and no grammar mistakes.
    
    Job Description Requirements:
    - Role: {jd.role}
    - Min Exp: {jd.min_experience_years}
    - Education: {jd.education}
    - Certs: {jd.certifications}
    - Domain: {jd.domain_keywords}
    
    Candidate Profile:
    - Total Exp: {candidate.total_experience_years}
    - Relevant Exp: {candidate.relevant_experience_years}
    - Education: {[e.model_dump() for e in candidate.education]}
    - Certs: {candidate.certifications}
    - Projects: {candidate.projects}
    - Experiences: {[e.model_dump() for e in candidate.experiences]}
    - Comm Quality (raw): {candidate.communication_quality}
    """
    
    return structured_llm.invoke(prompt)

def calculate_score(jd: JobDescription, candidate: Candidate) -> Dict[str, Any]:
    # 1. Skills Match (30%)
    all_jd_skills = jd.required_skills + jd.preferred_skills
    skills_match_result = match_skills(all_jd_skills, candidate.skills)
    
    # Calculate score out of 10
    skills_score_out_of_10 = (skills_match_result["match_percentage"] / 100) * 10
    
    # Get LLM reasoning for other dimensions
    llm_eval = get_llm_reasoning(jd, candidate)
    
    # Calculate weights
    weights = {
        "skills": 0.30,
        "experience": 0.25,
        "education": 0.15,
        "projects": 0.20,
        "communication": 0.10
    }
    
    # Final Python Math Calculation
    weighted_total = (
        (skills_score_out_of_10 * weights["skills"]) +
        (llm_eval.experience_score * weights["experience"]) +
        (llm_eval.education_score * weights["education"]) +
        (llm_eval.project_score * weights["projects"]) +
        (llm_eval.communication_score * weights["communication"])
    )
    
    # Scale from out of 10 to out of 100
    final_score_100 = round(weighted_total * 10, 2)
    
    recommendation = "No-Hire"
    if final_score_100 >= 75:
        recommendation = "Strong Hire"
    elif final_score_100 >= 60:
        recommendation = "Hire"
    elif final_score_100 >= 45:
        recommendation = "Needs Review"
        
    return {
        "candidate_id": candidate.id,
        "candidate_name": candidate.name,
        "final_score": final_score_100,
        "recommendation": recommendation,
        "dimensions": {
            "skills": {
                "score": round(skills_score_out_of_10, 1),
                "justification": f"Matched {len(skills_match_result['matched'])} out of {len(all_jd_skills)} skills.",
                "weight": weights["skills"]
            },
            "experience": {
                "score": llm_eval.experience_score,
                "justification": llm_eval.experience_justification,
                "weight": weights["experience"]
            },
            "education": {
                "score": llm_eval.education_score,
                "justification": llm_eval.education_justification,
                "weight": weights["education"]
            },
            "projects": {
                "score": llm_eval.project_score,
                "justification": llm_eval.project_justification,
                "weight": weights["projects"]
            },
            "communication": {
                "score": llm_eval.communication_score,
                "justification": llm_eval.communication_justification,
                "weight": weights["communication"]
            }
        }
    }
