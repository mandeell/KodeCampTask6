from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class User(BaseModel):
    """User model for authentication"""
    username: str
    password_hash: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserRegistration(BaseModel):
    """Model for user registration"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, description="Plain text password")
    email: Optional[str] = Field(None, description="User email")
    full_name: Optional[str] = Field(None, description="Full name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure123",
                "email": "john@example.com",
                "full_name": "John Doe"
            }
        }

class LoginRequest(BaseModel):
    """Model for login request"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure123"
            }
        }

class LoginResponse(BaseModel):
    """Model for login response with JWT token"""
    access_token: str
    token_type: str = "bearer"
    username: str
    expires_in: int  # seconds

class Note(BaseModel):
    """Note model with required fields"""
    id: int
    title: str
    content: str
    date: datetime
    username: str  # Owner of the note

class NoteCreate(BaseModel):
    """Model for creating a note"""
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, description="Note content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Meeting Notes",
                "content": "Discussed project timeline and deliverables. Next meeting scheduled for Friday."
            }
        }

class NoteUpdate(BaseModel):
    """Model for updating a note"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Meeting Notes",
                "content": "Updated content with action items and deadlines."
            }
        }

class NotesResponse(BaseModel):
    """Model for notes list response"""
    notes: List[Note]
    total_notes: int
    username: str

class Token(BaseModel):
    """Token model for JWT"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data model for JWT payload"""
    username: Optional[str] = None