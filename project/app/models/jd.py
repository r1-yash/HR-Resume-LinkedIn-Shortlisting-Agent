from typing import List, Optional
from pydantic import BaseModel, Field

class JobDescription(BaseModel):
    role: str = Field(description="The job title or role.")
    required_skills: List[str] = Field(description="Must-have skills for the role.")
    preferred_skills: List[str] = Field(description="Good-to-have or preferred skills.")
    min_experience_years: float = Field(description="Minimum years of experience required.")
    education: List[str] = Field(description="Educational degrees or qualifications required.")
    certifications: List[str] = Field(description="Specific certifications required.")
    domain_keywords: List[str] = Field(description="Keywords related to the industry or domain.")
    communication_requirements: List[str] = Field(description="Expectations regarding communication skills.")
