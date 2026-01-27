from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class CalendarEvent(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    job_application_id: str
    title: str
    type: str  # interview / followup / deadline
    start_time: datetime
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
