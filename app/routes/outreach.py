from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.services.outreach_engine import add_outreach_contact
from app.models.outreach_contact import OutreachContact
import app.database as database
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.outreach import OutreachContactCreate, OutreachContactResponse

router = APIRouter(prefix="/outreach", tags=["outreach"])


@router.post("/", response_model=OutreachContactResponse)
async def create_contact(
    contact_data: OutreachContactCreate, current_user: User = Depends(get_current_user)
):
    """Create a new outreach contact."""
    db = database.db

    job_app = await db.job_applications.find_one(
        {"_id": contact_data.job_application_id, "user_id": current_user.id}
    )

    if not job_app:
        raise HTTPException(status_code=404, detail="Job application not found")

    contact = await add_outreach_contact(
        contact_data.job_application_id,
        contact_data.name,
        contact_data.role,
        contact_data.company,
        contact_data.linkedin_url,
        contact_data.email,
    )

    await db.outreach_contacts.insert_one(contact.model_dump(by_alias=True))

    return OutreachContactResponse(
        id=contact.id,
        name=contact.name,
        role=contact.role,
        company=contact.company,
        linkedin_url=contact.linkedin_url,
        email=contact.email,
        contacted=contact.contacted,
    )


@router.get("/", response_model=List[OutreachContactResponse])
async def list_contacts(
    job_application_id: str, current_user: User = Depends(get_current_user)
):
    """List all outreach contacts for a job application."""
    db = database.db

    job_app = await db.job_applications.find_one(
        {"_id": job_application_id, "user_id": current_user.id}
    )

    if not job_app:
        raise HTTPException(status_code=404, detail="Job application not found")

    contacts = await db.outreach_contacts.find(
        {"job_application_id": job_application_id}
    ).to_list(100)

    return [
        OutreachContactResponse(
            id=c["_id"],
            name=c["name"],
            role=c["role"],
            company=c["company"],
            linkedin_url=c.get("linkedin_url"),
            email=c.get("email"),
            contacted=c.get("contacted", False),
        )
        for c in contacts
    ]
