from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models import User
import json
import hashlib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBasic()

USERS_FILE = "users.json"

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = "job_tracker_salt"  # Should be random and stored securely in production
    return hashlib.sha256((password + salt).encode()).hexdigest()

def load_users():
    """Load users from JSON file with proper error handling"""
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        return {}
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading users file: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading users file: {e}")
        return {}

def save_users(users_dict):
    """Save users to JSON file with proper error handling"""
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users_dict, f, indent=2)
    except IOError as e:
        logger.error(f"Error saving users file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save user data")
    except Exception as e:
        logger.error(f"Unexpected error saving users file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save user data")

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)) -> User:
    """Authenticate user using HTTP Basic Auth"""
    users = load_users()
    
    if credentials.username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"}
        )

    user_data = users[credentials.username]
    stored_hash = user_data["password_hash"]
    input_hash = hash_password(credentials.password)

    if input_hash != stored_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"}
        )
    
    return User(
        username=credentials.username,
        password_hash=stored_hash,
        email=user_data.get("email"),
        full_name=user_data.get("full_name")
    )

def get_current_user(user: User = Depends(authenticate_user)) -> User:
    """Get current authenticated user - main dependency for protected routes"""
    return user

def register_user(username: str, password: str, email: str = None, full_name: str = None):
    """Register a new user"""
    users = load_users()
    
    if username in users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Validate username
    if len(username.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long"
        )
    
    # Validate password
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Hash password and create user
    hashed_password = hash_password(password)
    users[username] = {
        "password_hash": hashed_password,
        "email": email,
        "full_name": full_name
    }
    
    save_users(users)
    logger.info(f"User {username} registered successfully")
    
    return {
        "message": "User registered successfully",
        "username": username
    }