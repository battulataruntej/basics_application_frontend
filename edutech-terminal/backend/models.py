"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
from datetime import datetime

class UserCreate(BaseModel):
    """User registration model"""
    email: EmailStr
    username: str
    password: str

class User(BaseModel):
    """User model"""
    id: str
    email: EmailStr
    username: str
    role: str = "student"
    created_at: datetime

class Token(BaseModel):
    """JWT token model"""
    access_token: str
    token_type: str

class TerminalSession(BaseModel):
    """Terminal session model"""
    id: str
    user_id: str
    pod_name: str
    created_at: float
    last_activity: float
    status: str

class Lab(BaseModel):
    """Lab model"""
    id: str
    course_id: str
    title: str
    description: str
    environment_type: str
    commands: List[str]

class Course(BaseModel):
    """Course model"""
    id: str
    title: str
    description: str
    difficulty: str
    labs: List[Dict]