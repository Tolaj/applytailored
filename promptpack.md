# PromptPack Output

**Root:** `D:/projects/python_/applytailored`
**Generated:** 2026-01-27T14:42:52.208Z

---

## 1) Folder Structure

```txt
.
├─ app/
│  ├─ __pycache__/
│  │  ├─ config.cpython-314.pyc
│  │  ├─ database.cpython-314.pyc
│  │  └─ main.cpython-314.pyc
│  ├─ config.py
│  ├─ database.py
│  ├─ dependencies/
│  │  ├─ __pycache__/
│  │  │  └─ auth.cpython-314.pyc
│  │  └─ auth.py
│  ├─ main.py
│  ├─ models/
│  │  ├─ __pycache__/
│  │  │  ├─ calendar_event.cpython-314.pyc
│  │  │  ├─ generated_asset.cpython-314.pyc
│  │  │  ├─ job_application.cpython-314.pyc
│  │  │  ├─ outreach_contact.cpython-314.pyc
│  │  │  └─ user.cpython-314.pyc
│  │  ├─ application_question.py
│  │  ├─ base_resume.py
│  │  ├─ calendar_event.py
│  │  ├─ experience_response.py
│  │  ├─ followup.py
│  │  ├─ generated_asset.py
│  │  ├─ job_application.py
│  │  ├─ outreach_contact.py
│  │  └─ user.py
│  ├─ routes/
│  │  ├─ __pycache__/
│  │  │  ├─ auth.cpython-314.pyc
│  │  │  ├─ calendar.cpython-314.pyc
│  │  │  ├─ dashboard.cpython-314.pyc
│  │  │  ├─ generation.cpython-314.pyc
│  │  │  ├─ job_application.cpython-314.pyc
│  │  │  └─ outreach.cpython-314.pyc
│  │  ├─ auth.py
│  │  ├─ calendar.py
│  │  ├─ dashboard.py
│  │  ├─ generation.py
│  │  ├─ job_application.py
│  │  └─ outreach.py
│  ├─ schemas/
│  │  ├─ __pycache__/
│  │  │  ├─ auth.cpython-314.pyc
│  │  │  ├─ generation.cpython-314.pyc
│  │  │  ├─ job_application.cpython-314.pyc
│  │  │  └─ outreach.cpython-314.pyc
│  │  ├─ auth.py
│  │  ├─ generation.py
│  │  ├─ job_application.py
│  │  └─ outreach.py
│  ├─ services/
│  │  ├─ __pycache__/
│  │  │  ├─ calendar_service.cpython-314.pyc
│  │  │  ├─ cold_email_engine.cpython-314.pyc
│  │  │  ├─ cover_letter_engine.cpython-314.pyc
│  │  │  ├─ outreach_engine.cpython-314.pyc
│  │  │  └─ resume_engine.cpython-314.pyc
│  │  ├─ auth_service.py
│  │  ├─ calendar_service.py
│  │  ├─ cold_email_engine.py
│  │  ├─ cover_letter_engine.py
│  │  ├─ file_service.py
│  │  ├─ followup_engine.py
│  │  ├─ job_application_service.py
│  │  ├─ outreach_engine.py
│  │  ├─ pdf_service.py
│  │  ├─ question_answer_engine.py
│  │  └─ resume_engine.py
│  ├─ static/
│  │  └─ js/
│  │     └─ auth.js
│  ├─ templates/
│  │  ├─ application/
│  │  │  ├─ assets.html
│  │  │  ├─ calendar.html
│  │  │  ├─ detail.html
│  │  │  ├─ outreach.html
│  │  │  └─ questions.html
│  │  ├─ auth/
│  │  │  ├─ login.html
│  │  │  └─ signup.html
│  │  ├─ base.html
│  │  ├─ dashboard/
│  │  │  ├─ index.html
│  │  │  └─ new_application.html
│  │  └─ partials/
│  │     ├─ navbar.html
│  │     └─ sidebar.html
│  └─ utils/
│     ├─ __pycache__/
│     │  ├─ ids.cpython-314.pyc
│     │  └─ security.cpython-314.pyc
│     ├─ ids.py
│     ├─ latex_escape.py
│     └─ security.py
├─ README.md
├─ requirements.txt
├─ scripts/
│  ├─ __pycache__/
│  │  ├─ init_db.cpython-314.pyc
│  │  ├─ init_indexes.cpython-314.pyc
│  │  └─ seed_data.cpython-314.pyc
│  ├─ init_db.py
│  ├─ init_indexes.py
│  └─ seed_data.py
└─ storage/
   ├─ base_resumes/
   │  └─ resume_v1.tex
   └─ generated/
```

<!-- PAGE BREAK: FILE CONTENTS BELOW -->

## 2) File Contents


### app/__pycache__/config.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/__pycache__/database.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/__pycache__/main.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "job_platform")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
GENERATED_DIR = os.path.join(STORAGE_DIR, "generated")

# Ensure directories exist
os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

```

### app/database.py

```python
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DB_NAME

db_client = None
db = None


async def connect_db():
    global db_client, db
    db_client = AsyncIOMotorClient(MONGO_URI)
    db = db_client[DB_NAME]
    print("✓ Connected to MongoDB")


async def close_db():
    global db_client
    if db_client:
        db_client.close()
        print("✓ MongoDB connection closed")

```

### app/dependencies/__pycache__/auth.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/dependencies/auth.py

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.utils.security import decode_access_token
import app.database as database
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    db = database.db
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available",
        )

    user_data = await db.users.find_one({"_id": user_id})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return User(**user_data)

```

### app/main.py

```python
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

```

### app/models/__pycache__/calendar_event.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/models/__pycache__/generated_asset.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/models/__pycache__/job_application.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/models/__pycache__/outreach_contact.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/models/__pycache__/user.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/models/application_question.py

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class ApplicationQuestion(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    job_application_id: str
    question: str
    answer: str
    ai_generated: bool = True
    edited_by_user: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True

```

### app/models/base_resume.py

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class BaseResume(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    user_id: str
    title: str
    description: str
    latex_template_path: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True

```

### app/models/calendar_event.py

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class CalendarEvent(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    job_application_id: str
    title: str
    type: str  # interview / followup / deadline
    start_time: datetime
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True

```

### app/models/experience_response.py

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class ExperienceResponse(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    job_application_id: str
    experience_type: str  # backend / cloud / leadership etc
    description: str
    ai_generated: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True

```

### app/models/followup.py

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class Followup(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    outreach_contact_id: str
    job_application_id: str
    message_asset_id: Optional[str] = None
    status: str = "pending"
    followup_number: int = 1
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

```

### app/models/generated_asset.py

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class GeneratedAsset(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    job_application_id: str
    user_id: str
    type: str  # resume / cover_letter / cold_email / followup / question_answer
    title: str
    content_text: str
    pdf_path: Optional[str] = None
    tex_path: Optional[str] = None
    ai_model: str
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True

```

### app/models/job_application.py

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class JobApplication(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    user_id: str
    company_name: str
    job_title: str
    job_description: str
    job_url: Optional[str] = None
    status: str = "draft"
    base_resume_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True

```

### app/models/outreach_contact.py

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class OutreachContact(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    job_application_id: str
    name: str
    role: str
    company: str
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    priority: str = "medium"
    contacted: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True

```

### app/models/user.py

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone
from app.utils.ids import generate_id


class User(BaseModel):
    id: str = Field(default_factory=generate_id, alias="_id")
    email: EmailStr
    name: str
    password_hash: str
    role: str = "user"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}

```

### app/routes/__pycache__/auth.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/routes/__pycache__/calendar.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/routes/__pycache__/dashboard.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/routes/__pycache__/generation.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/routes/__pycache__/job_application.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/routes/__pycache__/outreach.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/routes/auth.py

```python
from fastapi import APIRouter, Form, HTTPException, status, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from app.utils.security import hash_password, verify_password, create_access_token
from app.models.user import User
from fastapi.templating import Jinja2Templates
from app.schemas.auth import SignupRequest, LoginRequest, TokenResponse
import app.database as database

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/signup", response_class=HTMLResponse)
async def signup_view(request: Request):
    """Display signup page."""
    return templates.TemplateResponse("auth/signup.html", {"request": request})


@router.post("/signup", response_model=dict)
async def signup_post(
    email: str = Form(...), name: str = Form(...), password: str = Form(...)
):
    """Create a new user account."""
    db = database.db
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available",
        )

    existing_user = await db.users.find_one({"email": email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    user = User(email=email, name=name, password_hash=hash_password(password))
    await db.users.insert_one(user.model_dump(by_alias=True))
    return {"message": "User created successfully", "user_id": user.id}


@router.get("/login", response_class=HTMLResponse)
async def login_view(request: Request):
    """Display login page."""
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login", response_model=TokenResponse)
async def login_post(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT token."""
    db = database.db
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available",
        )

    # OAuth2PasswordRequestForm uses 'username' field, but we store email
    # So we search by email using the username field value
    user_data = await db.users.find_one({"email": form_data.username})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = User(**user_data)
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.id})
    return TokenResponse(access_token=access_token, token_type="bearer")

```

### app/routes/calendar.py

```python
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

```

### app/routes/dashboard.py

```python
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

```

### app/routes/generation.py

```python
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

```

### app/routes/job_application.py

```python
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

```

### app/routes/outreach.py

```python
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

```

### app/schemas/__pycache__/auth.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/schemas/__pycache__/generation.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/schemas/__pycache__/job_application.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/schemas/__pycache__/outreach.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/schemas/auth.py

```python
from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr
    name: str
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

```

### app/schemas/generation.py

```python
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    job_application_id: str
    user_id: str
    job_description: str = ""


class GenerateResponse(BaseModel):
    id: str
    title: str
    type: str
    content_text: str
    pdf_path: str = ""

```

### app/schemas/job_application.py

```python
from pydantic import BaseModel
from typing import Optional


class JobApplicationCreate(BaseModel):
    company_name: str
    job_title: str
    job_description: str
    job_url: Optional[str] = None


class JobApplicationResponse(BaseModel):
    id: str
    company_name: str
    job_title: str
    job_description: str
    status: str
    base_resume_id: Optional[str] = None

```

### app/schemas/outreach.py

```python
from pydantic import BaseModel
from typing import Optional


class OutreachContactCreate(BaseModel):
    job_application_id: str
    name: str
    role: str
    company: str
    linkedin_url: Optional[str] = None
    email: Optional[str] = None


class OutreachContactResponse(BaseModel):
    id: str
    name: str
    role: str
    company: str
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    contacted: bool

```

### app/services/__pycache__/calendar_service.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/services/__pycache__/cold_email_engine.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/services/__pycache__/cover_letter_engine.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/services/__pycache__/outreach_engine.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/services/__pycache__/resume_engine.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/services/auth_service.py

```python
from app.database import db
from app.models.user import User
from app.utils.security import hash_password, verify_password, create_access_token
from typing import Optional


async def create_user(email: str, name: str, password: str) -> User:
    """Create a new user."""
    hashed = hash_password(password)
    user = User(email=email, name=name, password_hash=hashed)
    await db.users.insert_one(user.model_dump(by_alias=True))
    return user


async def authenticate_user(email: str, password: str) -> Optional[str]:
    """Authenticate a user and return JWT token."""
    user_data = await db.users.find_one({"email": email})
    if not user_data:
        return None

    user = User(**user_data)
    if not verify_password(password, user.password_hash):
        return None

    # Create access token with user_id in the 'sub' claim
    token = create_access_token(data={"sub": user.id})
    return token

```

### app/services/calendar_service.py

```python
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

```

### app/services/cold_email_engine.py

```python
from app.models.generated_asset import GeneratedAsset
from anthropic import Anthropic
from app.config import ANTHROPIC_API_KEY
import app.database as database


async def generate_cold_email(job_application_id: str, user_id: str) -> GeneratedAsset:
    """Generate a cold email for networking/outreach."""
    db = database.db
    job_app = await db.job_applications.find_one({"_id": job_application_id})

    if ANTHROPIC_API_KEY and job_app:
        try:
            client = Anthropic(api_key=ANTHROPIC_API_KEY)

            prompt = f"""Write a professional cold email for networking purposes.

Company: {job_app.get('company_name', 'the company')}
Position: {job_app.get('job_title', 'the position')}

The email should:
1. Be concise and respectful of the recipient's time
2. Express genuine interest in the company and role
3. Request a brief informational conversation
4. Be friendly but professional
5. Be no more than 3-4 short paragraphs

Do not include [Your Name] or placeholders - just write the email body."""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            content = message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            content = f"Cold email for job app {job_application_id}"
    else:
        content = f"Cold email for job app {job_application_id}\n\nNote: Set ANTHROPIC_API_KEY for AI-generated content."

    return GeneratedAsset(
        job_application_id=job_application_id,
        user_id=user_id,
        type="cold_email",
        title="Cold Email",
        content_text=content,
        ai_model="claude-sonnet-4-20250514",
    )

```

### app/services/cover_letter_engine.py

```python
from app.models.generated_asset import GeneratedAsset
from anthropic import Anthropic
from app.config import ANTHROPIC_API_KEY


async def generate_cover_letter(
    job_application_id: str, user_id: str, job_description: str
) -> GeneratedAsset:
    """
    Generate a tailored cover letter using Claude AI.
    """

    if ANTHROPIC_API_KEY:
        try:
            client = Anthropic(api_key=ANTHROPIC_API_KEY)

            prompt = f"""Write a professional cover letter for this job:

Job Description:
{job_description}

Create a compelling cover letter that:
1. Shows enthusiasm for the position
2. Highlights relevant skills and experience
3. Demonstrates knowledge of the role requirements
4. Is concise and professional (3-4 paragraphs)

Format it as a formal business letter."""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            content = message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            content = f"Tailored cover letter for job app {job_application_id}"
    else:
        content = f"Tailored cover letter for job app {job_application_id}\n\nNote: Set ANTHROPIC_API_KEY for AI-generated content."

    return GeneratedAsset(
        job_application_id=job_application_id,
        user_id=user_id,
        type="cover_letter",
        title="Cover Letter",
        content_text=content,
        ai_model="claude-sonnet-4-20250514",
    )

```

### app/services/file_service.py

```python
import os
from app.config import GENERATED_DIR
import uuid


def save_text_file(content: str, subfolder: str, prefix: str) -> str:
    """Save text content to a file."""
    folder = os.path.join(GENERATED_DIR, subfolder)
    os.makedirs(folder, exist_ok=True)
    filename = f"{prefix}_{uuid.uuid4().hex}.txt"
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

```

### app/services/followup_engine.py

```python
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

```

### app/services/job_application_service.py

```python
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

```

### app/services/outreach_engine.py

```python
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

```

### app/services/pdf_service.py

```python
import subprocess
import os


def compile_tex_to_pdf(tex_path: str) -> str:
    """
    Compile a LaTeX file to PDF.
    Requires pdflatex to be installed on the system.
    """
    if not os.path.exists(tex_path):
        raise FileNotFoundError(f"LaTeX file not found: {tex_path}")

    cwd = os.path.dirname(tex_path)

    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_path],
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise Exception(f"PDF compilation failed: {e}")
    except FileNotFoundError:
        raise Exception(
            "pdflatex not found. Please install TeX distribution (e.g., TeX Live, MiKTeX)"
        )

    pdf_path = tex_path.replace(".tex", ".pdf")

    if not os.path.exists(pdf_path):
        raise Exception("PDF compilation produced no output file")

    return pdf_path

```

### app/services/question_answer_engine.py

```python
from app.models.application_question import ApplicationQuestion
from anthropic import Anthropic
from app.config import ANTHROPIC_API_KEY


async def generate_question_answer(
    job_application_id: str, question: str
) -> ApplicationQuestion:
    """
    Generate an AI answer to an application question.
    """

    if ANTHROPIC_API_KEY:
        try:
            client = Anthropic(api_key=ANTHROPIC_API_KEY)

            prompt = f"""You are helping someone answer a job application question. 
Provide a thoughtful, professional answer.

Question: {question}

Provide a clear, concise answer that would be appropriate for a job application.
Keep it to 2-3 paragraphs."""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            answer = message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            answer = f"AI generated answer for question: {question}"
    else:
        answer = f"AI generated answer for question: {question}\n\nNote: Set ANTHROPIC_API_KEY for AI-generated content."

    return ApplicationQuestion(
        job_application_id=job_application_id,
        question=question,
        answer=answer,
        ai_generated=True,
    )

```

### app/services/resume_engine.py

```python
from app.models.generated_asset import GeneratedAsset
from anthropic import Anthropic
from app.config import ANTHROPIC_API_KEY
import os


async def generate_resume(
    job_application_id: str, user_id: str, job_description: str
) -> GeneratedAsset:
    """
    Generate a tailored resume using Claude AI.

    This is a placeholder implementation. In production, you would:
    1. Fetch user's base resume from database
    2. Parse the job description
    3. Call Claude API to generate tailored content
    4. Compile to PDF if needed
    """

    if ANTHROPIC_API_KEY:
        try:
            client = Anthropic(api_key=ANTHROPIC_API_KEY)

            prompt = f"""Generate a professional resume summary tailored for this job description:

Job Description:
{job_description}

Create a compelling summary that highlights relevant skills and experience for this position. 
Keep it concise and professional (3-4 sentences)."""

            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            content = message.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            content = f"Tailored resume for job app {job_application_id}\n\nJob Description Summary:\n{job_description[:200]}..."
    else:
        content = f"Tailored resume for job app {job_application_id}\n\nNote: Set ANTHROPIC_API_KEY for AI-generated content."

    return GeneratedAsset(
        job_application_id=job_application_id,
        user_id=user_id,
        type="resume",
        title="Tailored Resume",
        content_text=content,
        ai_model="claude-sonnet-4-20250514",
    )

```

### app/static/js/auth.js

```javascript
/**
 * Authentication utility functions
 */

/**
 * Get the stored access token
 * @returns {string|null} The access token or null if not found
 */
function getAccessToken() {
    return localStorage.getItem('access_token');
}

/**
 * Check if user is authenticated
 * @returns {boolean} True if token exists, false otherwise
 */
function isAuthenticated() {
    return getAccessToken() !== null;
}

/**
 * Redirect to login page if not authenticated
 */
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = '/auth/login';
        return false;
    }
    return true;
}

/**
 * Make an authenticated fetch request
 * @param {string} url - The URL to fetch
 * @param {object} options - Fetch options
 * @returns {Promise<Response>}
 */
async function fetchWithAuth(url, options = {}) {
    const token = getAccessToken();

    if (!token) {
        throw new Error('No access token found');
    }

    // Merge headers with Authorization header
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    // If unauthorized, redirect to login
    if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/auth/login';
        throw new Error('Unauthorized - redirecting to login');
    }

    return response;
}

/**
 * Logout user by removing token and redirecting
 */
function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/auth/login';
}

/**
 * Make an authenticated API call and return JSON
 * @param {string} url - The URL to fetch
 * @param {object} options - Fetch options
 * @returns {Promise<any>}
 */
async function apiCall(url, options = {}) {
    const response = await fetchWithAuth(url, options);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || `Request failed with status ${response.status}`);
    }

    return response.json();
}

/**
 * GET request with authentication
 * @param {string} url - The URL to fetch
 * @returns {Promise<any>}
 */
async function apiGet(url) {
    return apiCall(url, { method: 'GET' });
}

/**
 * POST request with authentication
 * @param {string} url - The URL to fetch
 * @param {object} data - Data to send in the request body
 * @returns {Promise<any>}
 */
async function apiPost(url, data) {
    return apiCall(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
}

/**
 * PUT request with authentication
 * @param {string} url - The URL to fetch
 * @param {object} data - Data to send in the request body
 * @returns {Promise<any>}
 */
async function apiPut(url, data) {
    return apiCall(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
}

/**
 * DELETE request with authentication
 * @param {string} url - The URL to fetch
 * @returns {Promise<any>}
 */
async function apiDelete(url) {
    return apiCall(url, { method: 'DELETE' });
}

```

### app/templates/application/assets.html

```html
{% extends "base.html" %}
{% block title %}Assets{% endblock %}
{% block content %}
<h1 class="text-2xl font-bold mb-4">Generated Assets</h1>
<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    {% for asset in assets %}
    <div class="bg-white p-4 rounded shadow">
        <h2 class="font-bold">{{ asset.title }} ({{ asset.type }})</h2>
        <pre class="bg-gray-100 p-2 rounded mt-2">{{ asset.content_text }}</pre>
        {% if asset.pdf_path %}
        <a href="{{ asset.pdf_path }}" class="text-blue-600 hover:underline mt-2 block">Download PDF</a>
        {% endif %}
    </div>
    {% endfor %}
</div>
{% endblock %}

```

### app/templates/application/calendar.html

```html
{% extends "base.html" %}
{% block title %}Calendar{% endblock %}
{% block content %}
<h1 class="text-2xl font-bold mb-4">Calendar Events</h1>
<div class="space-y-4">
    {% for event in events %}
    <div class="bg-white p-4 rounded shadow">
        <h2 class="font-bold">{{ event.title }} ({{ event.type }})</h2>
        <p>Start: {{ event.start_time }}</p>
        {% if event.end_time %}
        <p>End: {{ event.end_time }}</p>
        {% endif %}
        {% if event.notes %}
        <p>Notes: {{ event.notes }}</p>
        {% endif %}
    </div>
    {% endfor %}
</div>
{% endblock %}

```

### app/templates/application/detail.html

```html
{% extends "base.html" %}
{% block title %}Job Application Detail{% endblock %}
{% block content %}
<h1 class="text-2xl font-bold mb-4">{{ application.company_name }} - {{ application.job_title }}</h1>
<div class="bg-white p-6 rounded shadow">
    <h2 class="font-bold text-lg mb-2">Job Description</h2>
    <p class="mb-4">{{ application.job_description }}</p>
    
    <a href="/application/assets/{{ application.id }}" class="text-blue-600 hover:underline">View Generated Assets</a>
</div>
{% endblock %}

```

### app/templates/application/outreach.html

```html
{% extends "base.html" %}
{% block title %}Outreach{% endblock %}
{% block content %}
<h1 class="text-2xl font-bold mb-4">Outreach Contacts</h1>
<div class="space-y-4">
    {% for contact in contacts %}
    <div class="bg-white p-4 rounded shadow flex justify-between items-center">
        <div>
            <h2 class="font-bold">{{ contact.name }} - {{ contact.role }}</h2>
            <p>{{ contact.company }}</p>
            {% if contact.linkedin_url %}
            <a href="{{ contact.linkedin_url }}" class="text-blue-600 hover:underline">LinkedIn</a>
            {% endif %}
        </div>
        <div>
            {% if contact.contacted %}
            <span class="text-green-600 font-bold">Contacted</span>
            {% else %}
            <span class="text-red-600 font-bold">Pending</span>
            {% endif %}
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}

```

### app/templates/application/questions.html

```html
{% extends "base.html" %}
{% block title %}Questions{% endblock %}
{% block content %}
<h1 class="text-2xl font-bold mb-4">Application Questions</h1>
<div class="space-y-4">
    {% for q in questions %}
    <div class="bg-white p-4 rounded shadow">
        <h2 class="font-bold mb-2">{{ q.question }}</h2>
        <p>{{ q.answer }}</p>
    </div>
    {% endfor %}
</div>
{% endblock %}

```

### app/templates/auth/login.html

```html
{% extends "base.html" %}
{% block title %}Login{% endblock %}
{% block content %}
<div class="max-w-md mx-auto bg-white p-6 rounded shadow">
    <h2 class="text-2xl font-bold mb-4">Login</h2>
    
    <!-- Error message display -->
    <div id="error-message" class="hidden bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
        <span id="error-text"></span>
    </div>
    
    <!-- Success message display -->
    <div id="success-message" class="hidden bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4" role="alert">
        <span id="success-text"></span>
    </div>
    
    <form id="loginForm" class="space-y-4">
        <input 
            type="email" 
            id="email" 
            name="email" 
            placeholder="Email" 
            class="w-full border px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" 
            required
        >
        <input 
            type="password" 
            id="password" 
            name="password" 
            placeholder="Password" 
            class="w-full border px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" 
            required
        >
        <button 
            type="submit" 
            id="loginButton"
            class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
            Login
        </button>
    </form>
    
    <p class="mt-4 text-center text-gray-600">
        Don't have an account? <a href="/auth/signup" class="text-blue-600 hover:underline">Sign up</a>
    </p>
</div>

<script>
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const loginButton = document.getElementById('loginButton');
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const successDiv = document.getElementById('success-message');
    const successText = document.getElementById('success-text');
    
    // Hide previous messages
    errorDiv.classList.add('hidden');
    successDiv.classList.add('hidden');
    
    // Disable button during request
    loginButton.disabled = true;
    loginButton.textContent = 'Logging in...';
    
    try {
        // OAuth2 expects form data with 'username' and 'password' fields
        const formData = new URLSearchParams();
        formData.append('username', email);  // OAuth2 uses 'username' field for email
        formData.append('password', password);
        
        const response = await fetch('/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }
        
        // Store the access token in localStorage
        localStorage.setItem('access_token', data.access_token);
        
        // Show success message
        successText.textContent = 'Login successful! Redirecting...';
        successDiv.classList.remove('hidden');
        
        // Redirect to dashboard after a brief delay
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1000);
        
    } catch (error) {
        // Show error message
        errorText.textContent = error.message || 'An error occurred during login';
        errorDiv.classList.remove('hidden');
        
        // Re-enable button
        loginButton.disabled = false;
        loginButton.textContent = 'Login';
    }
});
</script>
{% endblock %}

```

### app/templates/auth/signup.html

```html
{% extends "base.html" %}
{% block title %}Signup{% endblock %}
{% block content %}
<div class="max-w-md mx-auto bg-white p-6 rounded shadow">
    <h2 class="text-2xl font-bold mb-4">Create Account</h2>
    
    <!-- Error message display -->
    <div id="error-message" class="hidden bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4" role="alert">
        <span id="error-text"></span>
    </div>
    
    <!-- Success message display -->
    <div id="success-message" class="hidden bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4" role="alert">
        <span id="success-text"></span>
    </div>
    
    <form id="signupForm" class="space-y-4">
        <input 
            type="text" 
            id="name" 
            name="name" 
            placeholder="Full Name" 
            class="w-full border px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" 
            required
        >
        <input 
            type="email" 
            id="email" 
            name="email" 
            placeholder="Email" 
            class="w-full border px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" 
            required
        >
        <input 
            type="password" 
            id="password" 
            name="password" 
            placeholder="Password (min 6 characters)" 
            class="w-full border px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500" 
            minlength="6"
            required
        >
        <button 
            type="submit" 
            id="signupButton"
            class="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
            Sign Up
        </button>
    </form>
    
    <p class="mt-4 text-center text-gray-600">
        Already have an account? <a href="/auth/login" class="text-blue-600 hover:underline">Login</a>
    </p>
</div>

<script>
document.getElementById('signupForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const signupButton = document.getElementById('signupButton');
    const errorDiv = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const successDiv = document.getElementById('success-message');
    const successText = document.getElementById('success-text');
    
    // Hide previous messages
    errorDiv.classList.add('hidden');
    successDiv.classList.add('hidden');
    
    // Disable button during request
    signupButton.disabled = true;
    signupButton.textContent = 'Creating account...';
    
    try {
        const formData = new URLSearchParams();
        formData.append('name', name);
        formData.append('email', email);
        formData.append('password', password);
        
        const response = await fetch('/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Signup failed');
        }
        
        // Show success message
        successText.textContent = 'Account created successfully! Redirecting to login...';
        successDiv.classList.remove('hidden');
        
        // Redirect to login after a brief delay
        setTimeout(() => {
            window.location.href = '/auth/login';
        }, 2000);
        
    } catch (error) {
        // Show error message
        errorText.textContent = error.message || 'An error occurred during signup';
        errorDiv.classList.remove('hidden');
        
        // Re-enable button
        signupButton.disabled = false;
        signupButton.textContent = 'Sign Up';
    }
});
</script>
{% endblock %}

```

### app/templates/base.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Job Application Platform{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 font-sans">
    <div class="min-h-screen">
        {% block content %}{% endblock %}
    </div>
    
    <!-- Auth utility script for authenticated pages -->
    <script src="/static/js/auth.js"></script>
</body>
</html>

```

### app/templates/dashboard/index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Dashboard - Job Application Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <!-- Loading State -->
    <div id="loading" class="flex items-center justify-center min-h-screen">
        <div class="text-center">
            <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p class="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
    </div>

    <!-- Main Content (hidden initially) -->
    <div id="content" class="hidden">
        <!-- Navbar -->
        <nav class="bg-white shadow px-4 py-3 flex justify-between items-center">
            <div class="text-xl font-bold">JobAppAI</div>
            <div>
                <span class="text-gray-700 mr-4">Welcome, <span id="userName"></span></span>
                <button onclick="logout()" class="text-red-600 hover:underline">Logout</button>
            </div>
        </nav>

        <div class="flex">
            <!-- Sidebar -->
            <aside class="w-64 bg-white shadow p-4 min-h-screen">
                <ul class="space-y-2">
                    <li><a href="/dashboard" class="block p-2 rounded bg-blue-100 text-blue-700 font-semibold">Dashboard</a></li>
                    <li><a href="/job_applications/new" class="block p-2 rounded hover:bg-gray-100">New Application</a></li>
                    <li><a href="/calendar" class="block p-2 rounded hover:bg-gray-100">Calendar</a></li>
                    <li><a href="/outreach" class="block p-2 rounded hover:bg-gray-100">Outreach</a></li>
                </ul>
            </aside>

            <!-- Main Content -->
            <main class="flex-1 p-6">
                <div class="mb-6 flex justify-between items-center">
                    <h1 class="text-3xl font-bold text-gray-800">Job Applications</h1>
                    <a href="/job_applications/new" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                        + New Application
                    </a>
                </div>

                <!-- Applications Container -->
                <div id="applicationsContainer"></div>
            </main>
        </div>
    </div>

    <script>
        // Check authentication and load dashboard
        async function loadDashboard() {
            const token = localStorage.getItem('access_token');
            
            // If no token, redirect to login
            if (!token) {
                window.location.href = '/auth/login';
                return;
            }

            try {
                // Fetch dashboard data with auth token
                const response = await fetch('/api/dashboard', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        // Token expired or invalid
                        localStorage.removeItem('access_token');
                        window.location.href = '/auth/login';
                        return;
                    }
                    throw new Error('Failed to load dashboard');
                }

                const data = await response.json();
                
                // Update UI with user data
                document.getElementById('userName').textContent = data.user.name;
                
                // Render applications
                renderApplications(data.applications);
                
                // Hide loading, show content
                document.getElementById('loading').classList.add('hidden');
                document.getElementById('content').classList.remove('hidden');
                
            } catch (error) {
                console.error('Dashboard error:', error);
                alert('Failed to load dashboard. Please try logging in again.');
                localStorage.removeItem('access_token');
                window.location.href = '/auth/login';
            }
        }

        function renderApplications(applications) {
            const container = document.getElementById('applicationsContainer');
            
            if (!applications || applications.length === 0) {
                container.innerHTML = `
                    <div class="bg-white shadow rounded-lg p-8 text-center">
                        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <h3 class="mt-2 text-sm font-medium text-gray-900">No applications yet</h3>
                        <p class="mt-1 text-sm text-gray-500">Get started by creating a new job application.</p>
                        <div class="mt-6">
                            <a href="/job_applications/new" class="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                                + New Application
                            </a>
                        </div>
                    </div>
                `;
                return;
            }

            const statusColors = {
                'applied': 'bg-green-100 text-green-800',
                'interview': 'bg-blue-100 text-blue-800',
                'rejected': 'bg-red-100 text-red-800',
                'draft': 'bg-yellow-100 text-yellow-800'
            };

            const rows = applications.map(app => `
                <tr class="hover:bg-gray-50">
                    <td class="py-4 px-6 text-sm font-medium text-gray-900">${app.company_name}</td>
                    <td class="py-4 px-6 text-sm text-gray-700">${app.job_title}</td>
                    <td class="py-4 px-6">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusColors[app.status] || 'bg-gray-100 text-gray-800'}">
                            ${app.status}
                        </span>
                    </td>
                    <td class="py-4 px-6 text-sm">
                        <a href="/job_applications/${app._id}" class="text-blue-600 hover:underline mr-3">View</a>
                        <a href="/job_applications/${app._id}/edit" class="text-green-600 hover:underline">Edit</a>
                    </td>
                </tr>
            `).join('');

            container.innerHTML = `
                <div class="bg-white shadow rounded-lg overflow-hidden">
                    <table class="min-w-full">
                        <thead class="bg-gray-50">
                            <tr>
                                <th class="py-3 px-6 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                                <th class="py-3 px-6 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job Title</th>
                                <th class="py-3 px-6 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th class="py-3 px-6 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                            ${rows}
                        </tbody>
                    </table>
                </div>
            `;
        }

        function logout() {
            localStorage.removeItem('access_token');
            window.location.href = '/auth/login';
        }

        // Load dashboard when page loads
        window.addEventListener('DOMContentLoaded', loadDashboard);
    </script>
</body>
</html>

```

### app/templates/dashboard/new_application.html

```html
{% extends "base.html" %}
{% block title %}New Job Application{% endblock %}
{% block content %}
<h1 class="text-2xl font-bold mb-4">New Job Application</h1>
<form action="/job_applications" method="post" class="space-y-4 bg-white p-6 rounded shadow max-w-lg">
    <input type="text" name="company_name" placeholder="Company Name" class="w-full border px-3 py-2 rounded" required>
    <input type="text" name="job_title" placeholder="Job Title" class="w-full border px-3 py-2 rounded" required>
    <textarea name="job_description" placeholder="Job Description" class="w-full border px-3 py-2 rounded" rows="5" required></textarea>
    <button type="submit" class="bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700">Create Application</button>
</form>
{% endblock %}

```

### app/templates/partials/navbar.html

```html
<nav class="bg-white shadow px-4 py-3 flex justify-between items-center">
    <div class="text-xl font-bold">JobAppAI</div>
    <div>
        <a href="/auth/login" class="text-blue-600 hover:underline mr-4">Login</a>
        <a href="/auth/signup" class="text-blue-600 hover:underline">Signup</a>
    </div>
</nav>

```

### app/templates/partials/sidebar.html

```html
<aside class="w-64 bg-white shadow p-4 hidden md:block">
    <ul class="space-y-2">
        <li><a href="/" class="block p-2 rounded hover:bg-gray-200">Dashboard</a></li>
        <li><a href="/job_applications" class="block p-2 rounded hover:bg-gray-200">Job Applications</a></li>
        <li><a href="/generate" class="block p-2 rounded hover:bg-gray-200">Generate Assets</a></li>
        <li><a href="/outreach" class="block p-2 rounded hover:bg-gray-200">Outreach</a></li>
        <li><a href="/calendar" class="block p-2 rounded hover:bg-gray-200">Calendar</a></li>
    </ul>
</aside>

```

### app/utils/__pycache__/ids.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/utils/__pycache__/security.cpython-314.pyc

(Skipped: binary or unreadable file)


### app/utils/ids.py

```python
import uuid


def generate_id() -> str:
    """Generate a unique ID for database documents."""
    return str(uuid.uuid4())

```

### app/utils/latex_escape.py

```python
"""Utility functions for escaping LaTeX special characters."""


def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters in a string.

    Args:
        text: The text to escape

    Returns:
        The escaped text safe for LaTeX
    """
    if not text:
        return ""

    # Define LaTeX special characters and their escaped versions
    replacements = {
        "\\": r"\textbackslash{}",
        "{": r"\{",
        "}": r"\}",
        "$": r"\$",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }

    # Apply replacements
    result = text
    for char, replacement in replacements.items():
        result = result.replace(char, replacement)

    return result

```

### app/utils/security.py

```python
# app/utils/security.py
import bcrypt
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from typing import Optional, Dict


def hash_password(password: str) -> str:
    """Hash a password using bcrypt directly."""
    # Convert password to bytes
    password_bytes = password.encode("utf-8")
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    # Convert to bytes
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    # Verify
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

```

### README.md

```markdown


```

### requirements.txt

```text
fastapi
uvicorn[standard]
pydantic
pydantic-settings
python-dotenv
motor
jinja2
python-multipart
bcrypt==4.0.1
passlib[bcrypt]==1.7.4
python-jose[cryptography]
pydantic[email]
PyJWT
anthropic

```

### scripts/__pycache__/init_db.cpython-314.pyc

(Skipped: binary or unreadable file)


### scripts/__pycache__/init_indexes.cpython-314.pyc

(Skipped: binary or unreadable file)


### scripts/__pycache__/seed_data.cpython-314.pyc

(Skipped: binary or unreadable file)


### scripts/init_db.py

```python
import asyncio
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app.database as database
from app.models.user import User
from app.utils.security import hash_password
from app.utils.ids import generate_id


async def init_indexes_and_seed():
    """Initialize database indexes and seed with test data."""
    # Connect to DB
    await database.connect_db()

    # Access db from the module AFTER connection
    db = database.db
    if db is None:
        raise Exception("DB connection failed!")

    print("✓ Connected to MongoDB")

    # ------------------------
    # 1) Create Indexes
    # ------------------------
    print("Creating indexes...")
    await db.users.create_index("email", unique=True)
    await db.job_applications.create_index("user_id")
    await db.generated_assets.create_index("job_application_id")
    await db.generated_assets.create_index("user_id")
    await db.outreach_contacts.create_index("job_application_id")
    await db.followups.create_index("outreach_contact_id")
    await db.application_questions.create_index("job_application_id")
    await db.calendar_events.create_index("job_application_id")
    await db.base_resumes.create_index("user_id")
    await db.experience_responses.create_index("job_application_id")
    print("✓ Indexes created")

    # ------------------------
    # 2) Seed Data
    # ------------------------
    print("Seeding data...")

    # Check if test user already exists
    existing = await db.users.find_one({"email": "test@example.com"})

    if not existing:
        # Create test user
        test_user = User(
            email="test@example.com",
            name="Test User",
            password_hash=hash_password("password123"),
        )
        await db.users.insert_one(test_user.model_dump(by_alias=True))
        user_id = test_user.id
        print(f"✓ Test user created with ID: {user_id}")
        print(f"  Email: test@example.com")
        print(f"  Password: password123")
    else:
        user_id = existing["_id"]
        print(f"✓ Test user already exists with ID: {user_id}")

    # Example: Base Resume for test user
    if await db.base_resumes.count_documents({"user_id": user_id}) == 0:
        await db.base_resumes.insert_one(
            {
                "_id": generate_id(),
                "user_id": user_id,
                "title": "Default Resume",
                "description": "Seeded default resume",
                "latex_template_path": "storage/base_resumes/resume_v1.tex",
            }
        )
        print("✓ Default base resume created")
    else:
        print("✓ Default base resume already exists")

    # Close DB
    await database.close_db()
    print("\n✓ Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(init_indexes_and_seed())

```

### scripts/init_indexes.py

```python
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app.database as database


async def init_indexes():
    """Initialize database indexes."""
    # Connect to DB
    await database.connect_db()

    # Access the database AFTER connection
    db = database.db
    if db is None:
        raise Exception("DB connection failed!")

    # Create indexes
    print("Creating indexes...")
    await db.users.create_index("email", unique=True)
    await db.job_applications.create_index("user_id")
    await db.generated_assets.create_index("job_application_id")
    await db.outreach_contacts.create_index("job_application_id")

    print("✓ Indexes initialized successfully!")

    # Close DB connection
    await database.close_db()


if __name__ == "__main__":
    asyncio.run(init_indexes())

```

### scripts/seed_data.py

```python
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app.database as database
from app.models.user import User
from app.models.job_application import JobApplication
from app.utils.security import hash_password


async def seed_data():
    """Seed the database with test data."""
    await database.connect_db()

    # Access db from the module AFTER connection
    db = database.db
    if db is None:
        raise Exception("DB connection failed!")

    # Create a test user
    test_user = User(
        email="test2@example.com",  # Different email to avoid conflicts
        name="Test User 2",
        password_hash=hash_password("password123"),
        role="user",
    )
    await db.users.insert_one(test_user.model_dump(by_alias=True))
    print(f"✓ Test user created with ID: {test_user.id}")

    # Create a sample job application
    job_app = JobApplication(
        user_id=test_user.id,
        company_name="Tech Corp",
        job_title="Software Engineer",
        job_description="Develop amazing software with cutting-edge technologies",
        status="draft",
    )
    await db.job_applications.insert_one(job_app.model_dump(by_alias=True))
    print(f"✓ Job application created with ID: {job_app.id}")

    print("✓ Seed data inserted successfully!")
    await database.close_db()


if __name__ == "__main__":
    asyncio.run(seed_data())

```

### storage/base_resumes/resume_v1.tex

```


```