from typing import List, Optional, Any
from pydantic import BaseModel, Field

class Experience(BaseModel):
    title: str = ""
    company: str = ""
    duration: str = ""
    description: str = ""

class Education(BaseModel):
    degree: str = ""
    institution: str = ""
    year: str = ""

import uuid

class Candidate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the candidate")
    name: str = "Unknown"
    email: str = "Unknown"
    phone: str = "Unknown"
    education: List[Education] = []
    certifications: List[str] = []
    total_experience_years: float = 0.0
    relevant_experience_years: float = 0.0
    skills: List[str] = []
    projects: List[str] = []
    communication_quality: str = "Unknown"
    linkedin_url: Optional[str] = None
    resume_source: str = "Unknown"
    raw_text: str = ""
    experiences: List[Experience] = []
