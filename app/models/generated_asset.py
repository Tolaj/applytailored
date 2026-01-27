from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class GeneratedAsset(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    job_application_id: str
    user_id: str
    type: str  # resume / cover_letter / cold_email / followup / question_answer
    title: str
    content_text: str
    pdf_path: Optional[str] = None
    tex_path: Optional[str] = None
    ai_model: str
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
