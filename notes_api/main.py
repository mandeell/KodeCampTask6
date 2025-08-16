from fastapi import FastAPI, HTTPException, status, Depends
from models import (
    UserRegistration, LoginRequest, LoginResponse, NoteCreate, NoteUpdate,
    Note, NotesResponse, User
)
from auth import (
    get_current_user, register_user, authenticate_user, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
import json
import os
import logging
from typing import List, Optional
from datetime import datetime, timedelta

app = FastAPI(
    title="Notes API with JWT Authentication",
    description="A secure notes management API using JWT Bearer token authentication",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NOTES_FILE = "notes.json"

def load_notes():
    """Load notes from JSON file with proper error handling"""
    try:
        if os.path.exists(NOTES_FILE):
            with open(NOTES_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        return []
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading notes file: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error loading notes file: {e}")
        return []

def save_notes(notes_list):
    """Save notes to JSON file with proper error handling"""
    try:
        with open(NOTES_FILE, "w") as f:
            json.dump(notes_list, f, indent=2, default=str)  # default=str for datetime serialization
    except IOError as e:
        logger.error(f"Error saving notes file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save notes data")
    except Exception as e:
        logger.error(f"Unexpected error saving notes file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save notes data")

def get_next_note_id():
    """Get the next available note ID"""
    notes = load_notes()
    if not notes:
        return 1
    return max(note["id"] for note in notes) + 1

def get_user_notes(username: str):
    """Get all notes for a specific user"""
    notes = load_notes()
    return [note for note in notes if note["username"] == username]

def find_note_by_id(note_id: int, username: str):
    """Find a note by ID that belongs to the specified user"""
    notes = load_notes()
    for note in notes:
        if note["id"] == note_id and note["username"] == username:
            return note
    return None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Notes API with JWT Authentication",
        "version": "1.0.0",
        "description": "Secure notes management with JWT Bearer tokens",
        "endpoints": {
            "register": "POST /register/",
            "login": "POST /login/ (returns JWT token)",
            "add_note": "POST /notes/ (requires Bearer token)",
            "get_notes": "GET /notes/ (requires Bearer token)",
            "update_note": "PUT /notes/{id} (requires Bearer token)",
            "delete_note": "DELETE /notes/{id} (requires Bearer token)"
        },
        "authentication": {
            "type": "JWT Bearer Token",
            "header": "Authorization: Bearer <token>",
            "token_expires": f"{ACCESS_TOKEN_EXPIRE_MINUTES} minutes"
        }
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
    """Authenticate user and return JWT token"""
    try:
        # Authenticate user
        user = authenticate_user(login_data.username, login_data.password)
        if not user:
            logger.warning(f"Failed login attempt for user: {login_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        logger.info(f"User {login_data.username} logged in successfully")
        
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            username=user.username,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )

@app.post('/notes/', status_code=status.HTTP_201_CREATED)
async def add_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_user)
):
    """Add a new note (requires JWT token)"""
    try:
        notes = load_notes()
        
        # Create new note
        new_note = {
            "id": get_next_note_id(),
            "title": note_data.title,
            "content": note_data.content,
            "date": datetime.utcnow().isoformat(),
            "username": current_user.username  # Automatically set to current user
        }
        
        notes.append(new_note)
        save_notes(notes)
        
        logger.info(f"Note '{note_data.title}' added by user {current_user.username}")
        
        return {
            "message": "Note added successfully",
            "note": new_note
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add note due to server error"
        )

@app.get('/notes/', response_model=NotesResponse)
async def get_notes(
    current_user: User = Depends(get_current_user),
    limit: Optional[int] = None,
    search: Optional[str] = None
):
    """Get all notes for the current user (requires JWT token)"""
    try:
        # Get only the current user's notes
        user_notes = get_user_notes(current_user.username)
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            user_notes = [
                note for note in user_notes 
                if search_lower in note["title"].lower() or search_lower in note["content"].lower()
            ]
        
        # Sort by date (newest first)
        user_notes.sort(key=lambda x: datetime.fromisoformat(x["date"]), reverse=True)
        
        # Apply limit if provided
        if limit and limit > 0:
            user_notes = user_notes[:limit]
        
        # Convert to Note objects
        notes_objects = []
        for note in user_notes:
            notes_objects.append(Note(
                id=note["id"],
                title=note["title"],
                content=note["content"],
                date=datetime.fromisoformat(note["date"]),
                username=note["username"]
            ))
        
        logger.info(f"Retrieved {len(notes_objects)} notes for user {current_user.username}")
        
        return NotesResponse(
            notes=notes_objects,
            total_notes=len(notes_objects),
            username=current_user.username
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving notes for {current_user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notes due to server error"
        )

@app.put('/notes/{note_id}')
async def update_note(
    note_id: int,
    update_data: NoteUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a note (requires JWT token, only owner can update)"""
    try:
        notes = load_notes()
        
        # Find the note
        note = find_note_by_id(note_id, current_user.username)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found or you don't have permission to access it"
            )
        
        # Update the note
        for i, note in enumerate(notes):
            if note["id"] == note_id and note["username"] == current_user.username:
                # Update only provided fields
                if update_data.title is not None:
                    notes[i]["title"] = update_data.title
                if update_data.content is not None:
                    notes[i]["content"] = update_data.content
                
                # Update the date to current time
                notes[i]["date"] = datetime.utcnow().isoformat()
                
                save_notes(notes)
                
                logger.info(f"Note {note_id} updated by user {current_user.username}")
                
                return {
                    "message": "Note updated successfully",
                    "note": notes[i]
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating note {note_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update note due to server error"
        )

@app.delete('/notes/{note_id}')
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a note (requires JWT token, only owner can delete)"""
    try:
        notes = load_notes()
        
        # Find and remove the note
        for i, note in enumerate(notes):
            if note["id"] == note_id and note["username"] == current_user.username:
                deleted_note = notes.pop(i)
                save_notes(notes)
                
                logger.info(f"Note {note_id} deleted by user {current_user.username}")
                
                return {
                    "message": "Note deleted successfully",
                    "deleted_note": deleted_note
                }
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or you don't have permission to delete it"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note {note_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete note due to server error"
        )

@app.get('/notes/{note_id}')
async def get_note(
    note_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get a specific note by ID (requires JWT token, only owner can access)"""
    try:
        note = find_note_by_id(note_id, current_user.username)
        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Note not found or you don't have permission to access it"
            )
        
        # Convert to Note object
        note_object = Note(
            id=note["id"],
            title=note["title"],
            content=note["content"],
            date=datetime.fromisoformat(note["date"]),
            username=note["username"]
        )
        
        logger.info(f"Note {note_id} retrieved by user {current_user.username}")
        
        return note_object
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving note {note_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve note due to server error"
        )