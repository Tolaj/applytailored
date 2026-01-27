from pydantic import BaseModel
from typing import Optional


class OutreachContactCreate(BaseModel):
    job_application_id: str
    name: str
    role: str
    company: str
    linkedin_url: Optional[str] = None
    email: Optional[str] = None


class OutreachContactResponse(BaseModel):
    id: str
    name: str
    role: str
    company: str
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    contacted: bool
