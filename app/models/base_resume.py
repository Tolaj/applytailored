from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class BaseResume(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    user_id: str
    title: str
    description: str
    latex_template_path: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
