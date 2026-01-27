from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from app.services.calendar_service import add_event
from app.models.calendar_event import CalendarEvent
import app.database as database
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.post("/", response_model=CalendarEvent)
async def create_event(
    job_application_id: str,
    title: str,
    type: str,
    start_time: datetime,
    end_time: datetime = None,
    notes: str = "",
    current_user: User = Depends(get_current_user),
):
    """Create a new calendar event."""
    db = database.db

    job_app = await db.job_applications.find_one(
        {"_id": job_application_id, "user_id": current_user.id}
    )

    if not job_app:
        raise HTTPException(status_code=404, detail="Job application not found")

    event = await add_event(
        job_application_id, title, type, start_time, end_time, notes
    )

    await db.calendar_events.insert_one(event.model_dump(by_alias=True))

    return event


@router.get("/", response_model=List[CalendarEvent])
async def list_events(
    job_application_id: str = None, current_user: User = Depends(get_current_user)
):
    """List calendar events, optionally filtered by job application."""
    db = database.db
    query = {}

    if job_application_id:
        job_app = await db.job_applications.find_one(
            {"_id": job_application_id, "user_id": current_user.id}
        )

        if not job_app:
            raise HTTPException(status_code=404, detail="Job application not found")

        query["job_application_id"] = job_application_id
    else:
        user_apps = await db.job_applications.find(
            {"user_id": current_user.id}
        ).to_list(1000)
        app_ids = [app["_id"] for app in user_apps]
        query["job_application_id"] = {"$in": app_ids}

    events = await db.calendar_events.find(query).to_list(100)
    return [CalendarEvent(**event) for event in events]
