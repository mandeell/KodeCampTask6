from fastapi import FastAPI, HTTPException, status, Depends
from models import (
    UserRegistration, LoginRequest, LoginResponse, JobApplicationCreate,
    JobApplicationUpdate, JobApplication, ApplicationsResponse, ApplicationStats,
    User, ApplicationStatus
)
from auth import get_current_user, register_user, hash_password, load_users
import json
import os
import logging
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="Job Application Tracker API",
    description="A secure API for tracking job applications with user-specific access",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

APPLICATIONS_FILE = "applications.json"

def load_applications():
    """Load applications from JSON file with proper error handling"""
    try:
        if os.path.exists(APPLICATIONS_FILE):
            with open(APPLICATIONS_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        return []
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading applications file: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error loading applications file: {e}")
        return []

def save_applications(applications_list):
    """Save applications to JSON file with proper error handling"""
    try:
        with open(APPLICATIONS_FILE, "w") as f:
            json.dump(applications_list, f, indent=2, default=str)  # default=str for datetime serialization
    except IOError as e:
        logger.error(f"Error saving applications file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save application data")
    except Exception as e:
        logger.error(f"Unexpected error saving applications file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save application data")

def get_next_application_id():
    """Get the next available application ID"""
    applications = load_applications()
    if not applications:
        return 1
    return max(app["id"] for app in applications) + 1

def get_user_applications(username: str):
    """Get all applications for a specific user"""
    applications = load_applications()
    return [app for app in applications if app["username"] == username]

def find_application_by_id(application_id: int, username: str):
    """Find an application by ID that belongs to the specified user"""
    applications = load_applications()
    for app in applications:
        if app["id"] == application_id and app["username"] == username:
            return app
    return None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Job Application Tracker API",
        "version": "1.0.0",
        "description": "Track your job applications securely",
        "endpoints": {
            "register": "POST /register/",
            "login": "POST /login/",
            "add_application": "POST /applications/",
            "get_applications": "GET /applications/",
            "update_application": "PUT /applications/{id}",
            "delete_application": "DELETE /applications/{id}",
            "get_stats": "GET /applications/stats/"
        },
        "features": [
            "Secure user authentication",
            "User-specific application access",
            "Full CRUD operations for applications",
            "Application statistics and insights"
        ]
    }

@app.post('/register/', status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegistration):
    """Register a new user"""
    try:
        result = register_user(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email,
            full_name=user_data.full_name
        )
        return result
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
    """Authenticate user credentials"""
    try:
        users = load_users()
        
        if login_data.username not in users:
            logger.warning(f"Login attempt with non-existent username: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        user_data = users[login_data.username]
        stored_hash = user_data["password_hash"]
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
            username=login_data.username,
            full_name=user_data.get("full_name")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )

@app.post('/applications/', status_code=status.HTTP_201_CREATED)
async def add_application(
    application_data: JobApplicationCreate,
    current_user: User = Depends(get_current_user)
):
    """Add a new job application (authenticated users only)"""
    try:
        applications = load_applications()
        
        # Create new application
        new_application = {
            "id": get_next_application_id(),
            "job_title": application_data.job_title,
            "company": application_data.company,
            "date_applied": application_data.date_applied.isoformat(),
            "status": application_data.status.value,
            "username": current_user.username,  # Automatically set to current user
            "description": application_data.description,
            "salary_range": application_data.salary_range,
            "location": application_data.location,
            "notes": application_data.notes
        }
        
        applications.append(new_application)
        save_applications(applications)
        
        logger.info(f"Application for '{application_data.job_title}' at '{application_data.company}' added by user {current_user.username}")
        
        return {
            "message": "Job application added successfully",
            "application": new_application
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding application: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add application due to server error"
        )

@app.get('/applications/', response_model=ApplicationsResponse)
async def get_applications(
    current_user: User = Depends(get_current_user),
    status_filter: Optional[ApplicationStatus] = None,
    company_filter: Optional[str] = None,
    limit: Optional[int] = None
):
    """Get all job applications for the current user (with optional filters)"""
    try:
        # Get only the current user's applications
        user_applications = get_user_applications(current_user.username)
        
        # Apply filters if provided
        filtered_applications = user_applications
        
        if status_filter:
            filtered_applications = [
                app for app in filtered_applications 
                if app["status"] == status_filter.value
            ]
        
        if company_filter:
            filtered_applications = [
                app for app in filtered_applications 
                if company_filter.lower() in app["company"].lower()
            ]
        
        # Apply limit if provided
        if limit and limit > 0:
            filtered_applications = filtered_applications[:limit]
        
        # Convert to JobApplication objects
        applications_objects = []
        for app in filtered_applications:
            applications_objects.append(JobApplication(
                id=app["id"],
                job_title=app["job_title"],
                company=app["company"],
                date_applied=datetime.fromisoformat(app["date_applied"]),
                status=ApplicationStatus(app["status"]),
                username=app["username"],
                description=app.get("description"),
                salary_range=app.get("salary_range"),
                location=app.get("location"),
                notes=app.get("notes")
            ))
        
        logger.info(f"Retrieved {len(applications_objects)} applications for user {current_user.username}")
        
        return ApplicationsResponse(
            applications=applications_objects,
            total_applications=len(applications_objects),
            username=current_user.username
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving applications for {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve applications due to server error"
        )

@app.put('/applications/{application_id}')
async def update_application(
    application_id: int,
    update_data: JobApplicationUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a job application (only the owner can update)"""
    try:
        applications = load_applications()
        
        # Find the application
        application = find_application_by_id(application_id, current_user.username)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found or you don't have permission to access it"
            )
        
        # Update the application
        for i, app in enumerate(applications):
            if app["id"] == application_id and app["username"] == current_user.username:
                # Update only provided fields
                if update_data.job_title is not None:
                    applications[i]["job_title"] = update_data.job_title
                if update_data.company is not None:
                    applications[i]["company"] = update_data.company
                if update_data.date_applied is not None:
                    applications[i]["date_applied"] = update_data.date_applied.isoformat()
                if update_data.status is not None:
                    applications[i]["status"] = update_data.status.value
                if update_data.description is not None:
                    applications[i]["description"] = update_data.description
                if update_data.salary_range is not None:
                    applications[i]["salary_range"] = update_data.salary_range
                if update_data.location is not None:
                    applications[i]["location"] = update_data.location
                if update_data.notes is not None:
                    applications[i]["notes"] = update_data.notes
                
                save_applications(applications)
                
                logger.info(f"Application {application_id} updated by user {current_user.username}")
                
                return {
                    "message": "Application updated successfully",
                    "application": applications[i]
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application {application_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update application due to server error"
        )

@app.delete('/applications/{application_id}')
async def delete_application(
    application_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a job application (only the owner can delete)"""
    try:
        applications = load_applications()
        
        # Find and remove the application
        for i, app in enumerate(applications):
            if app["id"] == application_id and app["username"] == current_user.username:
                deleted_app = applications.pop(i)
                save_applications(applications)
                
                logger.info(f"Application {application_id} deleted by user {current_user.username}")
                
                return {
                    "message": "Application deleted successfully",
                    "deleted_application": deleted_app
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or you don't have permission to delete it"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting application {application_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete application due to server error"
        )

@app.get('/applications/stats/', response_model=ApplicationStats)
async def get_application_stats(current_user: User = Depends(get_current_user)):
    """Get application statistics for the current user"""
    try:
        user_applications = get_user_applications(current_user.username)
        
        # Calculate statistics
        total_applications = len(user_applications)
        
        # Status breakdown
        status_breakdown = {}
        for status in ApplicationStatus:
            count = len([app for app in user_applications if app["status"] == status.value])
            status_breakdown[status.value] = count
        
        # Companies applied to
        companies = list(set(app["company"] for app in user_applications))
        
        # Recent applications (last 5)
        sorted_applications = sorted(
            user_applications,
            key=lambda x: datetime.fromisoformat(x["date_applied"]),
            reverse=True
        )
        recent_apps = []
        for app in sorted_applications[:5]:
            recent_apps.append(JobApplication(
                id=app["id"],
                job_title=app["job_title"],
                company=app["company"],
                date_applied=datetime.fromisoformat(app["date_applied"]),
                status=ApplicationStatus(app["status"]),
                username=app["username"],
                description=app.get("description"),
                salary_range=app.get("salary_range"),
                location=app.get("location"),
                notes=app.get("notes")
            ))
        
        logger.info(f"Statistics retrieved for user {current_user.username}")
        
        return ApplicationStats(
            username=current_user.username,
            total_applications=total_applications,
            status_breakdown=status_breakdown,
            companies_applied=companies,
            recent_applications=recent_apps
        )
    
    except Exception as e:
        logger.error(f"Error retrieving stats for {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics due to server error"
        )