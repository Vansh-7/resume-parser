from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# 1. Blueprint for Education
class Education(BaseModel):
    institution: str = Field(description="Name of the university, college, or school")
    degree: str = Field(description="The degree or certification obtained (e.g., B.Tech, High School)")
    time_period: Optional[str] = Field(default=None, description="Years of study or graduation year")
    grade: Optional[str] = Field(default=None, description="GPA, CGPA, or percentage if mentioned")

# 2. Blueprint for a single Job Experience
class Experience(BaseModel):
    company_name: str
    role: str
    time_period: str
    location: str
    description: str = Field(description="A short summary of what the candidate did")

# 3. Blueprint for a single Project
class Project(BaseModel):
    project_title: str
    time_period: Optional[str] = Field(default=None, description="When the project was done")
    link: Optional[str] = Field(default=None, description="GitHub repository or live website link")
    description: str = Field(description="A summary of the project and the technologies used")

# 4. Your Main Master Blueprint
class Resume(BaseModel):
    name: str = Field(..., description="The full name of the candidate")
    phone_no: str
    email: EmailStr
    
    # Using all your nested models here!
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list) 
    projects: list[Project] = Field(default_factory=list) 
    
    skills: list[str] = Field(default_factory=list)
    
# Final evalaution result
class MatchResult(BaseModel):
    match_percentage: int = Field(description="Match score from 0 to 100 based on fit")
    matching_skills: list[str] = Field(description="Skills candidate possesses that match the JD")
    missing_skills: list[str] = Field(description="Key skills required by JD but missing in resume")
    strengths: list[str] = Field(description="Key highlights and strong points of the candidate")
    summary: str = Field(description="Brief candidate evaluation summary from recruiter perspective")