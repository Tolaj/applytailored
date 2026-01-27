from fastapi import APIRouter, Depends, HTTPException
from app.services.resume_engine import generate_resume
from app.services.cover_letter_engine import generate_cover_letter
from app.services.cold_email_engine import generate_cold_email
import app.database as database
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.generation import GenerateRequest, GenerateResponse

router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("/resume", response_model=GenerateResponse)
async def generate_resume_route(
    request: GenerateRequest, current_user: User = Depends(get_current_user)
):
    """Generate a tailored resume for a job application."""
    db = database.db

    job_app = await db.job_applications.find_one(
        {"_id": request.job_application_id, "user_id": current_user.id}
    )

    if not job_app:
        raise HTTPException(status_code=404, detail="Job application not found")

    asset = await generate_resume(
        request.job_application_id,
        current_user.id,
        request.job_description or job_app.get("job_description", ""),
    )

    await db.generated_assets.insert_one(asset.model_dump(by_alias=True))

    return GenerateResponse(
        id=asset.id,
        title=asset.title,
        type=asset.type,
        content_text=asset.content_text,
        pdf_path=asset.pdf_path or "",
    )


@router.post("/cover_letter", response_model=GenerateResponse)
async def generate_cover_letter_route(
    request: GenerateRequest, current_user: User = Depends(get_current_user)
):
    """Generate a tailored cover letter for a job application."""
    db = database.db

    job_app = await db.job_applications.find_one(
        {"_id": request.job_application_id, "user_id": current_user.id}
    )

    if not job_app:
        raise HTTPException(status_code=404, detail="Job application not found")

    asset = await generate_cover_letter(
        request.job_application_id,
        current_user.id,
        request.job_description or job_app.get("job_description", ""),
    )

    await db.generated_assets.insert_one(asset.model_dump(by_alias=True))

    return GenerateResponse(
        id=asset.id,
        title=asset.title,
        type=asset.type,
        content_text=asset.content_text,
        pdf_path=asset.pdf_path or "",
    )


@router.post("/cold_email", response_model=GenerateResponse)
async def generate_cold_email_route(
    request: GenerateRequest, current_user: User = Depends(get_current_user)
):
    """Generate a cold email for a job application."""
    db = database.db

    job_app = await db.job_applications.find_one(
        {"_id": request.job_application_id, "user_id": current_user.id}
    )

    if not job_app:
        raise HTTPException(status_code=404, detail="Job application not found")

    asset = await generate_cold_email(request.job_application_id, current_user.id)
    await db.generated_assets.insert_one(asset.model_dump(by_alias=True))

    return GenerateResponse(
        id=asset.id,
        title=asset.title,
        type=asset.type,
        content_text=asset.content_text,
        pdf_path=asset.pdf_path or "",
    )
