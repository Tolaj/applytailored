from app.models.outreach_contact import OutreachContact


async def add_outreach_contact(
    job_application_id: str,
    name: str,
    role: str,
    company: str,
    linkedin_url=None,
    email=None,
) -> OutreachContact:
    """Create a new outreach contact."""
    return OutreachContact(
        job_application_id=job_application_id,
        name=name,
        role=role,
        company=company,
        linkedin_url=linkedin_url,
        email=email,
    )
