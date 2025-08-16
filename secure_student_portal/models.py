from pydantic import BaseModel, Field
from typing import List

class Student(BaseModel):
    """Model for student data stored in database"""
    username: str
    password_hash: str
    grades: List[float] = []

class StudentRegistration(BaseModel):
    """Model for student registration request"""
    username: str = Field(..., min_length=5, max_length=50, description="Username for the student")
    password: str = Field(..., min_length=6, description="Plain text password (will be hashed)")
    grades: List[float] = Field(default=[], description="Initial grades (optional)")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure123",
                "grades": [85.5, 92.0, 78.5]
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
    user_data: dict
