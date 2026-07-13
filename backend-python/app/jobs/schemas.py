from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# ---------------------------------------------------------
# Job Knowledge Base (JKB) Sub-Models
# ---------------------------------------------------------

class CompanyInfo(BaseModel):
    name: Optional[str] = Field(None, description="Name of the hiring company")
    about: Optional[str] = Field(None, description="Brief description of the company")
    industry: Optional[str] = Field(None, description="Industry sector")

class SalaryDetails(BaseModel):
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    currency: Optional[str] = "USD"
    period: Optional[str] = Field(None, description="e.g., yearly, monthly, hourly")

# ---------------------------------------------------------
# Main Job Knowledge Base (JKB) Model
# ---------------------------------------------------------

class JobKnowledgeBase(BaseModel):
    """
    The final, structured output of the Job Engine pipeline.
    Symmetrical to CandidateKnowledgeBase.
    """
    company: CompanyInfo = Field(default_factory=CompanyInfo)
    role: Optional[str] = Field(None, description="Job title")
    department: Optional[str] = Field(None, description="Department or team within the company")
    
    locations: List[str] = Field(default_factory=list, description="Physical locations")
    
    employment_type: Optional[Literal[
        "Full-time",
        "Part-time",
        "Contract",
        "Internship",
        "Temporary",
        "Freelance"
    ]] = Field(None, description="Employment contract type")

    work_mode: Optional[Literal[
        "Remote",
        "Hybrid",
        "On-site"
    ]] = Field(None, description="Physical working arrangement")
    
    experience_level: Optional[str] = Field(None, description="Entry-level, Mid-senior, Director, etc.")
    years_of_experience: Optional[str] = Field(None, description="Required years of experience (e.g., '3-5 years')")
    
    skills: List[str] = Field(default_factory=list, description="Extracted hard and soft skills")
    responsibilities: List[str] = Field(default_factory=list, description="Day-to-day tasks")
    
    education: List[str] = Field(default_factory=list, description="Required degrees or fields of study")
    qualifications: List[str] = Field(default_factory=list, description="Certifications and other requirements")
    
    benefits: List[str] = Field(default_factory=list, description="Perks, healthcare, equity, etc.")
    salary: SalaryDetails = Field(default_factory=SalaryDetails)
    keywords: List[str] = Field(default_factory=list, description="SEO or ATS parsing keywords")

# ---------------------------------------------------------
# API Request Schema
# ---------------------------------------------------------

class JobParseRequest(BaseModel):
    """
    Unified request schema for the POST /api/v1/job/parse endpoint.
    """
    source_type: Literal["text", "pdf", "url"] = Field(
        ..., 
        description="The medium of the input source."
    )
    content: str = Field(
        ..., 
        description="Raw text, a signed PDF URL, or a career page URL based on source_type."
    )