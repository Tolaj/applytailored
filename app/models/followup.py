from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class Followup(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    outreach_contact_id: str
    job_application_id: str
    message_asset_id: Optional[str] = None
    status: str = "pending"
    followup_number: int = 1
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
