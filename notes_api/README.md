# Notes API with JWT Authentication

A secure notes management API using JWT Bearer token authentication.

## Features

- **JWT Token Authentication**: Secure Bearer token authentication
- **User-Specific Notes**: Each user can only access their own notes
- **Full CRUD Operations**: Create, Read, Update, Delete notes
- **Token Expiration**: Configurable token expiration (default: 30 minutes)
- **Search Functionality**: Search notes by title or content
- **Data Persistence**: Notes stored in JSON files per user

## Core Requirements Implemented

✅ **Note class**: `title`, `content`, `date` fields  
✅ **POST /login/**: Returns JWT token  
✅ **POST /notes/**: Add note (requires token)  
✅ **GET /notes/**: View own notes (requires token)  
✅ **Notes stored in notes.json**: Per-user data storage  
✅ **JWT Bearer token dependency**: Secure route protection  

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn main:app --reload
```

3. Access the API documentation at: `http://localhost:8000/docs`

## API Endpoints

### Public Endpoints

- `GET /` - API information and endpoints
- `POST /register/` - Register a new user
- `POST /login/` - Authenticate and get JWT token

### Protected Endpoints (Require JWT Bearer Token)

- `POST /notes/` - Add a new note
- `GET /notes/` - Get all your notes (with optional search and limit)
- `GET /notes/{id}` - Get a specific note by ID
- `PUT /notes/{id}` - Update a specific note
- `DELETE /notes/{id}` - Delete a specific note

## Usage Examples

### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/register/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "noteuser",
       "password": "secure123",
       "email": "noteuser@example.com",
       "full_name": "Note User"
     }'
```

### 2. Login and Get JWT Token

```bash
curl -X POST "http://localhost:8000/login/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "noteuser",
       "password": "secure123"
     }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "username": "noteuser",
  "expires_in": 1800
}
```

### 3. Add a Note (with JWT Token)

```bash
curl -X POST "http://localhost:8000/notes/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
     -d '{
       "title": "Meeting Notes",
       "content": "Discussed project timeline and deliverables. Next meeting scheduled for Friday."
     }'
```

### 4. Get All Your Notes

```bash
curl -X GET "http://localhost:8000/notes/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### 5. Get Notes with Search and Limit

```bash
# Search notes containing "meeting"
curl -X GET "http://localhost:8000/notes/?search=meeting" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"

# Get only the latest 5 notes
curl -X GET "http://localhost:8000/notes/?limit=5" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### 6. Update a Note

```bash
curl -X PUT "http://localhost:8000/notes/1" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
     -d '{
       "title": "Updated Meeting Notes",
       "content": "Updated content with action items and deadlines."
     }'
```

### 7. Delete a Note

```bash
curl -X DELETE "http://localhost:8000/notes/1" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### 8. Get a Specific Note

```bash
curl -X GET "http://localhost:8000/notes/1" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## JWT Token Authentication

### How it Works

1. **Login**: Send username/password to `/login/` endpoint
2. **Receive Token**: Get JWT token in response
3. **Use Token**: Include token in `Authorization` header for protected routes
4. **Token Format**: `Authorization: Bearer <your_jwt_token>`

### Token Details

- **Algorithm**: HS256
- **Expiration**: 30 minutes (configurable)
- **Payload**: Contains username and expiration time
- **Security**: Tokens are signed and verified on each request

### Example Token Usage in Different Languages

#### JavaScript (Fetch API)
```javascript
const token = "your_jwt_token_here";

fetch("http://localhost:8000/notes/", {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

#### Python (Requests)
```python
import requests

token = "your_jwt_token_here"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.get("http://localhost:8000/notes/", headers=headers)
notes = response.json()
```

## Data Models

### Note Model
```json
{
  "id": 1,
  "title": "Meeting Notes",
  "content": "Discussed project timeline and deliverables.",
  "date": "2024-01-15T10:30:00.123456",
  "username": "noteuser"
}
```

### Login Response
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "username": "noteuser",
  "expires_in": 1800
}
```

### Notes List Response
```json
{
  "notes": [
    {
      "id": 1,
      "title": "Meeting Notes",
      "content": "Discussed project timeline...",
      "date": "2024-01-15T10:30:00.123456",
      "username": "noteuser"
    }
  ],
  "total_notes": 1,
  "username": "noteuser"
}
```

## Security Features

- **JWT Token Signing**: All tokens are cryptographically signed
- **Token Expiration**: Tokens automatically expire after 30 minutes
- **User Isolation**: Users can only access their own notes
- **Password Hashing**: Passwords are hashed with salt before storage
- **Bearer Token Validation**: All protected routes validate JWT tokens
- **Error Handling**: Secure error responses without information leakage

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `201` - Created successfully
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/expired token, invalid credentials)
- `404` - Not Found (note doesn't exist or no permission)
- `500` - Internal Server Error

### Common Error Responses

#### Invalid Token
```json
{
  "detail": "Could not validate credentials"
}
```

#### Expired Token
```json
{
  "detail": "Could not validate credentials"
}
```

#### Note Not Found
```json
{
  "detail": "Note not found or you don't have permission to access it"
}
```

## Data Files

- `users.json` - User accounts and authentication data
- `notes.json` - All notes (filtered by user in API responses)

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```