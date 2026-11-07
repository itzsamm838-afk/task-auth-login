import os
import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from supabase import Client, create_client

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Set SUPABASE_URL and SUPABASE_KEY in your .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
app = FastAPI(title="Auth Login & Protect API", version="1.0.0")
bearer = HTTPBearer(auto_error=False)

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

def as_dict(value):
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "dict"):
        return value.dict()
    return value if isinstance(value, dict) else {"value": str(value)}

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": "Email and password are required and must be valid"})

@app.exception_handler(HTTPException)
async def http_error_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})

@app.get("/")
def root():
    return {"name": "Auth Login & Protect API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/signup", status_code=201)
def signup(payload: AuthRequest):
    if not payload.email.strip() or not payload.password.strip():
        raise HTTPException(400, "Email and password cannot be empty")
    try:
        result = supabase.auth.sign_up({"email": payload.email, "password": payload.password})
        user = getattr(result, "user", None)
        if user is None:
            raise HTTPException(400, "Signup could not be completed")
        return {"user": as_dict(user)}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(400, "Signup failed. Check credentials and Supabase settings.")

@app.post("/auth/login")
def login(payload: AuthRequest):
    if not payload.email.strip() or not payload.password.strip():
        raise HTTPException(400, "Email and password cannot be empty")
    try:
        result = supabase.auth.sign_in_with_password({"email": payload.email, "password": payload.password})
        session = getattr(result, "session", None)
        if session is None:
            raise HTTPException(401, "Invalid login credentials")
        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "token_type": "bearer",
            "user": as_dict(getattr(result, "user", None))
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(401, "Invalid login credentials")

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials.strip():
        raise HTTPException(401, "Access token required")
    try:
        result = supabase.auth.get_user(credentials.credentials.strip())
        user = getattr(result, "user", None)
        if user is None:
            raise ValueError("No user returned")
        return user
    except Exception:
        raise HTTPException(401, "Invalid or expired token")

@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile")
def profile(user=Depends(get_current_user)):
    created = getattr(user, "created_at", None)
    return {"id": user.id, "email": user.email, "created_at": str(created) if created else None}

@app.get("/protected/dashboard")
def dashboard(user=Depends(get_current_user)):
    return {"message": "Welcome to the protected dashboard", "user_id": user.id}

@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
           user=Depends(get_current_user)):
    # Stateless bearer-token API: revoke this token through Supabase Auth.
    try:
        response = httpx.post(
            f"{SUPABASE_URL.rstrip('/')}/auth/v1/logout",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {credentials.credentials}"},
            timeout=15.0
        )
        if response.status_code not in (200, 204):
            raise HTTPException(401, "Logout failed or token is invalid")
    except HTTPException:
        raise
    except httpx.HTTPError:
        raise HTTPException(502, "Could not contact Supabase to log out")
    return None
