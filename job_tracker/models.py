from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    """Job application status enumeration"""
    APPLIED = "applied"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEWED = "interviewed"
    OFFER_RECEIVED = "offer_received"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

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
        schema_extra = {
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
        schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure123"
            }
        }

class LoginResponse(BaseModel):
    """Model for login response"""
    message: str
    username: str
    full_name: Optional[str] = None

class JobApplication(BaseModel):
    """Job application model"""
    id: int
    job_title: str
    company: str
    date_applied: datetime
    status: ApplicationStatus
    username: str  # Owner of the application
    description: Optional[str] = None
    salary_range: Optional[str] = None
    location: Optional[str] = None
    notes: Optional[str] = None

class JobApplicationCreate(BaseModel):
    """Model for creating a job application"""
    job_title: str = Field(..., min_length=1, max_length=200, description="Job title")
    company: str = Field(..., min_length=1, max_length=200, description="Company name")
    date_applied: datetime = Field(..., description="Date when application was submitted")
    status: ApplicationStatus = Field(default=ApplicationStatus.APPLIED, description="Application status")
    description: Optional[str] = Field(None, max_length=1000, description="Job description")
    salary_range: Optional[str] = Field(None, max_length=100, description="Salary range")
    location: Optional[str] = Field(None, max_length=200, description="Job location")
    notes: Optional[str] = Field(None, max_length=1000, description="Personal notes")
    
    class Config:
        schema_extra = {
            "example": {
                "job_title": "Senior Software Engineer",
                "company": "Tech Corp",
                "date_applied": "2024-01-15T10:30:00",
                "status": "applied",
                "description": "Full-stack development role with Python and React",
                "salary_range": "$80,000 - $120,000",
                "location": "San Francisco, CA",
                "notes": "Applied through company website"
            }
        }

class JobApplicationUpdate(BaseModel):
    """Model for updating a job application"""
    job_title: Optional[str] = Field(None, min_length=1, max_length=200)
    company: Optional[str] = Field(None, min_length=1, max_length=200)
    date_applied: Optional[datetime] = None
    status: Optional[ApplicationStatus] = None
    description: Optional[str] = Field(None, max_length=1000)
    salary_range: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        schema_extra = {
            "example": {
                "status": "interview_scheduled",
                "notes": "Phone interview scheduled for next Tuesday"
            }
        }

class ApplicationsResponse(BaseModel):
    """Model for applications list response"""
    applications: List[JobApplication]
    total_applications: int
    username: str

class ApplicationStats(BaseModel):
    """Model for application statistics"""
    username: str
    total_applications: int
    status_breakdown: dict
    companies_applied: List[str]
    recent_applications: List[JobApplication]