from app.models.calendar_event import CalendarEvent
from datetime import datetime
from typing import Optional


async def add_event(
    job_application_id: str,
    title: str,
    type: str,
    start_time: datetime,
    end_time: Optional[datetime] = None,
    notes: str = "",
) -> CalendarEvent:
    """Create a new calendar event."""
    return CalendarEvent(
        job_application_id=job_application_id,
        title=title,
        type=type,
        start_time=start_time,
        end_time=end_time,
        notes=notes,
    )
