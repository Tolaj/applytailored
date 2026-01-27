from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class User(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    email: EmailStr
    name: str
    password_hash: str
    role: str = "user"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
