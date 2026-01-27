from pydantic import BaseModel
from typing import Optional


class JobApplicationCreate(BaseModel):
    company_name: str
    job_title: str
    job_description: str
    job_url: Optional[str] = None


class JobApplicationResponse(BaseModel):
    id: str
    company_name: str
    job_title: str
    job_description: str
    status: str
    base_resume_id: Optional[str] = None
