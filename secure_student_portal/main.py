from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models import Student, StudentRegistration, LoginRequest, LoginResponse, GradesResponse
import json
import hashlib
import os
import logging

app = FastAPI(
    title="Secure Student Portal API",
    description="A FastAPI application for student grade management",
    version="1.0.0"
)

security = HTTPBasic()

STUDENTS_FILE = "students.json"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_students():
    """Load students from JSON file with proper error handling"""
    try:
        if os.path.exists(STUDENTS_FILE):
            with open(STUDENTS_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        return {}
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading students file: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading students file: {e}")
        return {}

def save_students(students_dict):
    """Save students to JSON file with proper error handling"""
    try:
        with open(STUDENTS_FILE, "w") as f:
            json.dump(students_dict, f, indent=2)
    except IOError as e:
        logger.error(f"Error saving students file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save student data")
    except Exception as e:
        logger.error(f"Unexpected error saving students file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save student data")

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = "secure_student_portal_salt"  # Should be random and stored securely
    return hashlib.sha256((password + salt).encode()).hexdigest()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    """Authenticate user using HTTP Basic Auth"""
    students = load_students()
    
    if credentials.username not in students:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"}
        )

    stored_hash = students[credentials.username]["password_hash"]
    input_hash = hash_password(credentials.password)

    if input_hash != stored_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"}
        )
    
    return credentials.username

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Secure Student Portal API",
        "version": "1.0.0",
        "endpoints": {
            "register": "POST /register/",
            "login": "POST /login/",
            "grades": "GET /grades/ (requires authentication)"
        }
    }

@app.post('/register/', status_code=status.HTTP_201_CREATED)
async def register(student_data: StudentRegistration):
    """Register a new student with proper validation and security"""
    try:
        # Load existing students
        students_dict = load_students()
        
        # Check if username already exists
        if student_data.username in students_dict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Username already exists"
            )
        
        # Validate username (basic validation)
        if len(student_data.username.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters long"
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
        
        logger.info(f"Student {student_data.username} registered successfully")
        
        return {
            'message': 'Student registered successfully',
            'username': student_data.username
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )

@app.post('/login/', response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Authenticate student credentials"""
    try:
        # Load students
        students_dict = load_students()
        
        # Check if user exists
        if login_data.username not in students_dict:
            logger.warning(f"Login attempt with non-existent username: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password using the same hashing function as registration
        stored_hash = students_dict[login_data.username]["password_hash"]
        input_hash = hash_password(login_data.password)
        
        if input_hash != stored_hash:
            logger.warning(f"Failed login attempt for user: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        logger.info(f"User {login_data.username} logged in successfully")
        
        return LoginResponse(
            message="Login successful",
            username=login_data.username
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )

@app.get('/grades/', response_model=GradesResponse)
async def get_grades(current_user: str = Depends(get_current_username)):
    """Get grades for the authenticated student"""
    try:
        # Load students
        students_dict = load_students()
        
        # Get user's grades
        if current_user not in students_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        grades = students_dict[current_user]["grades"]
        
        # Calculate average grade if grades exist
        average_grade = None
        if grades:
            average_grade = round(sum(grades) / len(grades), 2)
        
        logger.info(f"Grades retrieved for user: {current_user}")
        
        return GradesResponse(
            username=current_user,
            grades=grades,
            average_grade=average_grade
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving grades for {current_user}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve grades due to server error"
        )