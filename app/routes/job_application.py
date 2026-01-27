from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse
import app.database as database
from app.models.job_application import JobApplication
from fastapi.templating import Jinja2Templates
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.job_application import JobApplicationCreate, JobApplicationResponse

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/job_applications", tags=["job_applications"])


@router.get("/", response_class=HTMLResponse)
async def list_job_applications(
    request: Request, current_user: User = Depends(get_current_user)
):
    """List all job applications for the current user."""
    db = database.db
    applications = await db.job_applications.find({"user_id": current_user.id}).to_list(
        100
    )

    return templates.TemplateResponse(
        "dashboard/index.html",
        {"request": request, "applications": applications, "user": current_user},
    )


@router.post("/", response_model=JobApplicationResponse)
async def create_job_application(
    application_data: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new job application."""
    db = database.db

    application = JobApplication(
        user_id=current_user.id,
        company_name=application_data.company_name,
        job_title=application_data.job_title,
        job_description=application_data.job_description,
        job_url=application_data.job_url,
    )

    await db.job_applications.insert_one(application.model_dump(by_alias=True))

    return JobApplicationResponse(
        id=application.id,
        company_name=application.company_name,
        job_title=application.job_title,
        job_description=application.job_description,
        status=application.status,
        base_resume_id=application.base_resume_id,
    )


@router.get("/{application_id}", response_model=JobApplicationResponse)
async def get_job_application(
    application_id: str, current_user: User = Depends(get_current_user)
):
    """Get a specific job application."""
    db = database.db

    application_data = await db.job_applications.find_one(
        {"_id": application_id, "user_id": current_user.id}
    )

    if not application_data:
        raise HTTPException(status_code=404, detail="Job application not found")

    application = JobApplication(**application_data)
    return JobApplicationResponse(
        id=application.id,
        company_name=application.company_name,
        job_title=application.job_title,
        job_description=application.job_description,
        status=application.status,
        base_resume_id=application.base_resume_id,
    )
