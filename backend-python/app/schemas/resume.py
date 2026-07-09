from pydantic import BaseModel, HttpUrl
from uuid import UUID
from app.candidate.schemas import CandidateKnowledgeBase

class ResumeParseRequest(BaseModel):
    resume_file_id: UUID
    file_url: HttpUrl
    filename: str

class ResumeParseResponse(BaseModel):
    resume_file_id: UUID
    candidate: CandidateKnowledgeBase