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
