from app.models.followup import Followup
from datetime import datetime, timedelta, timezone


async def schedule_followup(
    outreach_contact_id: str, job_application_id: str, followup_number=1
) -> Followup:
    """Schedule a follow-up for an outreach contact."""
    scheduled_time = datetime.now(timezone.utc) + timedelta(
        days=followup_number * 3
    )  # Example spacing: 3 days per followup number

    return Followup(
        outreach_contact_id=outreach_contact_id,
        job_application_id=job_application_id,
        followup_number=followup_number,
        scheduled_at=scheduled_time,
    )
