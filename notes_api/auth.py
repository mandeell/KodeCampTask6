from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import User, TokenData
from jose import JWTError, jwt
from datetime import datetime, timedelta
import json
import hashlib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = "notes_api_secret_key_change_in_production"  # Should be in environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

USERS_FILE = "users.json"

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = "notes_api_salt"  # Should be random and stored securely in production
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

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return username"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    # Verify user still exists
    users = load_users()
    if token_data.username not in users:
        raise credentials_exception
    
    return token_data.username

def get_current_user(username: str = Depends(verify_token)) -> User:
    """Get current authenticated user from JWT token"""
    users = load_users()
    
    if username not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    user_data = users[username]
    return User(
        username=username,
        password_hash=user_data["password_hash"],
        email=user_data.get("email"),
        full_name=user_data.get("full_name")
    )

def authenticate_user(username: str, password: str):
    """Authenticate user with username and password"""
    users = load_users()
    
    if username not in users:
        return False
    
    user_data = users[username]
    stored_hash = user_data["password_hash"]
    input_hash = hash_password(password)
    
    if input_hash != stored_hash:
        return False
    
    return User(
        username=username,
        password_hash=stored_hash,
        email=user_data.get("email"),
        full_name=user_data.get("full_name")
    )

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