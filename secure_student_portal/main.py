from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models import Student, StudentRegistration, LoginResponse, LoginRequest
import json
import hashlib
import os
import logging

app = FastAPI()
security = HTTPBasic()

STUDENTS_FILE = "students.json"


def load_students():
    """Load students from JSON file with proper error handling"""
    try:
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        return {}
    except (json.JSONDecodeError, IOError) as e:
        return {}

def save_students(students_dict):
    """Save students to JSON file with proper error handling"""
    try:
        with open(STUDENTS_FILE, "w") as f:
            json.dump(students_dict, f, indent=2)
    except IOError as e:
        raise HTTPException(status_code=500, detail="Failed to save student data")

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    # In production, use bcrypt or similar with proper salt
    salt = "secure_student_portal_salt"  # Should be random and stored securely
    return hashlib.sha256((password + salt).encode()).hexdigest()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    students = load_students()
    if credentials.username not in students:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"}
        )

    stored_hash = students[credentials.username]["password_hash"]
    # Use the same hashing function as registration
    input_hash = hash_password(credentials.password)

    if input_hash != stored_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"}
        )
    return credentials.username


@app.post('/register/', status_code=status.HTTP_201_CREATED)
async def register(student_data: StudentRegistration):
    """Register a new student with proper validation and security"""
    # Load existing students
    students_dict = load_students()
    
    # Check if username already exists
    if student_data.username in students_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already exists"
        )
    
    # Validate username (basic validation)
    if len(student_data.username.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 5 characters long"
        )
    
    # Validate password
    if len(student_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Hash the password
    hashed_password = hash_password(student_data.password)
    
    # Create student record
    students_dict[student_data.username] = {
        'password_hash': hashed_password,
        'grades': student_data.grades
    }
    
    # Save to file
    save_students(students_dict)

    return {
        'message': 'Student registered successfully',
        'username': student_data.username
    }

@app.post('/login/', response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Simple login endpoint that validates credentials"""
    # Load students
    students_dict = load_students()

    # Check if user exists
    if login_data.username not in students_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Verify password using the same hashing function as registration
    stored_hash = students_dict[login_data.username]["password_hash"]
    input_hash = hash_password(login_data.password)

    if input_hash != stored_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Get user data (excluding password hash for security)
    user_data = {
        'username': login_data.username,
        'grades': students_dict[login_data.username]['grades']
    }

    return LoginResponse(
        message="Login successful",
        username=login_data.username,
        user_data=user_data
    )



