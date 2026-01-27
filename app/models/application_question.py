from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class ApplicationQuestion(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    job_application_id: str
    question: str
    answer: str
    ai_generated: bool = True
    edited_by_user: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
