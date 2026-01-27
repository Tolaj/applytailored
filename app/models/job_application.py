from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class JobApplication(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    user_id: str
    company_name: str
    job_title: str
    job_description: str
    job_url: Optional[str] = None
    status: str = "draft"
    base_resume_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
