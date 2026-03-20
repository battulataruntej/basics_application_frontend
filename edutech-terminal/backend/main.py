"""
Main FastAPI application with WebSocket support for terminal sessions
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
import asyncio
import uuid
import time
import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
import logging

# Import custom modules
from models import User, UserCreate, Token, TerminalSession, Course, Lab
from session_manager import SessionManager
from websocket_handler import TerminalConnection

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Initialize FastAPI app
app = FastAPI(title="EduTech Terminal Platform", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# In-memory databases (Replace with PostgreSQL/MongoDB in production)
users_db: Dict[str, Dict] = {}
sessions_db: Dict[str, Dict] = {}
courses_db: Dict[str, Dict] = {
    "course_1": {
        "id": "course_1",
        "title": "Linux Fundamentals",
        "description": "Master essential Linux commands and system administration",
        "difficulty": "beginner",
        "labs": [
            {
                "id": "lab_1",
                "title": "File System Navigation",
                "description": "Learn to navigate the Linux file system",
                "environment_type": "ubuntu",
                "commands": ["ls", "cd", "pwd", "mkdir", "touch"]
            }
        ]
    },
    "course_2": {
        "id": "course_2",
        "title": "DevOps with Docker & Kubernetes",
        "description": "Container orchestration and deployment",
        "difficulty": "intermediate",
        "labs": [
            {
                "id": "lab_2",
                "title": "Docker Basics",
                "description": "Build and run containers",
                "environment_type": "docker",
                "commands": ["docker build", "docker run", "docker ps"]
            }
        ]
    }
}

# Initialize session manager
session_manager = SessionManager()

# Authentication functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = users_db.get(user_id)
    if user is None:
        raise credentials_exception
    return user

# API Endpoints
@app.post("/signup", response_model=Token)
async def signup(user_data: UserCreate):
    """User registration"""
    # Check if user exists
    if any(u["email"] == user_data.email for u in users_db.values()):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)

    user = {
        "id": user_id,
        "email": user_data.email,
        "username": user_data.username,
        "password": hashed_password,
        "role": "student",
        "created_at": datetime.utcnow().isoformat()
    }

    users_db[user_id] = user

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """User login - accepts both username and email"""
    # Find user by username or email
    user = None
    for u in users_db.values():
        if u["username"] == form_data.username or u["email"] == form_data.username:
            user = u
            break

    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "role": current_user["role"]
    }

@app.get("/courses", response_model=List[Course])
async def get_courses(current_user: dict = Depends(get_current_user)):
    """Get available courses"""
    return list(courses_db.values())

@app.get("/courses/{course_id}")
async def get_course(course_id: str, current_user: dict = Depends(get_current_user)):
    """Get course details"""
    course = courses_db.get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.post("/sessions/create")
async def create_session(
    environment_type: str = "ubuntu",
    current_user: dict = Depends(get_current_user)
):
    """Create new terminal session"""
    session_id = await session_manager.create_session(
        current_user["id"],
        environment_type
    )

    return {
        "session_id": session_id,
        "status": "active",
        "websocket_url": f"ws://localhost:8000/ws/terminal/{session_id}"
    }

@app.get("/sessions")
async def get_sessions(current_user: dict = Depends(get_current_user)):
    """Get user's active sessions"""
    user_sessions = [
        s for s in sessions_db.values()
        if s["user_id"] == current_user["id"] and s["status"] == "active"
    ]
    return user_sessions

@app.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Terminate session"""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    await session_manager.terminate_session(session_id)
    return {"status": "terminated"}

@app.websocket("/ws/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for terminal I/O"""

    # Validate session exists
    session = await session_manager.get_session(session_id)
    if not session:
        await websocket.close(code=1008, reason="Invalid session")
        return

    # Create terminal connection
    terminal = TerminalConnection(websocket, session_id)
    await terminal.connect()

    # Handle terminal I/O
    try:
        await terminal.handle_terminal_io()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info(f"WebSocket closed for session {session_id}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "active_sessions": len(session_manager.active_sessions),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Starting EduTech Terminal Platform")

    # Start background task for session cleanup
    asyncio.create_task(session_manager.cleanup_inactive_sessions())

    # Create demo user
    demo_user_id = str(uuid.uuid4())
    users_db[demo_user_id] = {
        "id": demo_user_id,
        "email": "demo@edutech.com",
        "username": "demo",
        "password": hash_password("demo123"),
        "role": "student",
        "created_at": datetime.utcnow().isoformat()
    }
    logger.info("Demo user created: demo@edutech.com / demo123")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Shutting down EduTech Terminal Platform")

    # Cleanup all active sessions
    for session_id in list(session_manager.active_sessions.keys()):
        await session_manager.terminate_session(session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )