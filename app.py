import logging
from datetime import timedelta
from bson import ObjectId
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from auth import login_user
from models import User, UserCreate, UserRead
from typing import List
from routes import (
    fetch_all_users,
    fetch_user_by_id,
    create_user,
    update_user,
    remove_user,
    login
)
import motor.motor_asyncio
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

# Add rate limit exceeded handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = ['http://localhost:3000']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# CSRF configuration
class CsrfSettings(BaseModel):
    secret_key: str = "uE#8r$7zD3*Q8!jN^w@1*Z8^uB5&yE0m"

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

# MongoDB client setup
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://mongo:27017')

@app.on_event("startup")
async def startup_event():
    try:
        await client.admin.command("ping")
        logger.info("Successfully connected to MongoDB!")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/user", response_model=List[UserRead])
@limiter.limit("10/minute")
async def get_all_users(request: Request):
    logger.info("Fetching all users")
    return await fetch_all_users()

@app.get("/api/user/{user_id}", response_model=UserRead)
@limiter.limit("10/minute")
async def get_user_by_id(request: Request, user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(400, detail="Invalid user ID format")
    try:
        response = await fetch_user_by_id(user_id)
        if response:
            return response
        else:
            raise HTTPException(404, f"No user found with the ID {user_id}")
    except Exception as e:
        logger.error(f"Error fetching user by ID: {e}")
        raise HTTPException(500, detail="Internal Server Error")

@app.post("/api/user", response_model=UserRead)
@limiter.limit("5/minute")
async def post_user(request: Request, user: UserCreate, csrf_protect: CsrfProtect = Depends()):
    csrf_protect.validate_csrf(request)
    return await create_user(user)

@app.put("/api/user/{user_id}", response_model=UserRead)
@limiter.limit("5/minute")
async def update_existing_user(request: Request, user_id: str, user: UserCreate, csrf_protect: CsrfProtect = Depends()):
    csrf_protect.validate_csrf(request)
    if not ObjectId.is_valid(user_id):
        raise HTTPException(400, detail="Invalid user ID format")
    updated_user = await update_user(user_id, user)
    if not updated_user:
        raise HTTPException(404, detail="User not found")
    return updated_user

@app.delete("/api/user/{user_id}")
@limiter.limit("5/minute")
async def delete_user(request: Request, user_id: str, csrf_protect: CsrfProtect = Depends()):
    csrf_protect.validate_csrf(request)
    if not ObjectId.is_valid(user_id):
        raise HTTPException(400, detail="Invalid user ID format")
    success = await remove_user(user_id)
    if not success:
        raise HTTPException(404, detail="User not found")
    return {"detail": "User deleted successfully"}

@app.post("/token")
async def login(user: UserCreate):
    return await login_user(user)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['localhost', '127.0.0.1'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
