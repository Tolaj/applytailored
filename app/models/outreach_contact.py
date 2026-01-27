from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class OutreachContact(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    job_application_id: str
    name: str
    role: str
    company: str
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    priority: str = "medium"
    contacted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
