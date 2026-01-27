from app.models.job_application import JobApplication
from app.database import db
from typing import List


async def create_job_application(
    user_id: str, company_name: str, job_title: str, job_description: str
) -> JobApplication:
    """Create a new job application."""
    job_app = JobApplication(
        user_id=user_id,
        company_name=company_name,
        job_title=job_title,
        job_description=job_description,
    )
    await db.job_applications.insert_one(job_app.model_dump(by_alias=True))
    return job_app


async def list_job_applications(user_id: str) -> List[dict]:
    """List all job applications for a user."""
    return await db.job_applications.find({"user_id": user_id}).to_list(100)
