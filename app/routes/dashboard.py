from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
import app.database as database
from app.dependencies.auth import get_current_user
from app.models.user import User

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_view(request: Request):
    """Serve the dashboard HTML page (client-side rendered)."""
    return templates.TemplateResponse(
        "dashboard/index.html",
        {"request": request},
    )


@router.get("/api/dashboard")
async def dashboard_api(current_user: User = Depends(get_current_user)):
    """API endpoint to get dashboard data with authentication."""
    db = database.db

    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available",
        )

    # Fetch user's job applications
    applications = await db.job_applications.find({"user_id": current_user.id}).to_list(
        100
    )

    return {
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
        },
        "applications": applications,
    }
