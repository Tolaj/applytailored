from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class ExperienceResponse(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    job_application_id: str
    experience_type: str  # backend / cloud / leadership etc
    description: str
    ai_generated: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
