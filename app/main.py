from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.routes import auth, dashboard, job_application, generation, outreach, calendar
from app.database import connect_db, close_db
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    await connect_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="Job Application Platform",
    description="AI-powered job application management system",
    version="1.0.0",
    lifespan=lifespan,
)

# Mount static files (create directory if it doesn't exist)
static_dir = "app/static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(job_application.router)
app.include_router(generation.router)
app.include_router(outreach.router)
app.include_router(calendar.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Job Application Platform API is running.",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
