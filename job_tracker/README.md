# Job Application Tracker API

A secure FastAPI application for tracking job applications where each user can only see and manage their own applications.

## Features

- **Secure Authentication**: HTTP Basic Auth with password hashing
- **User-Specific Access**: Users can only see their own job applications
- **Full CRUD Operations**: Create, Read, Update, Delete job applications
- **Application Filtering**: Filter by status, company, or limit results
- **Statistics Dashboard**: Get insights about your job search progress
- **Data Persistence**: All data stored in JSON files

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

- `GET /` - API information and available endpoints
- `POST /register/` - Register a new user
- `POST /login/` - User authentication

### Protected Endpoints (Require Authentication)

- `POST /applications/` - Add a new job application
- `GET /applications/` - Get all your job applications (with optional filters)
- `PUT /applications/{id}` - Update a specific job application
- `DELETE /applications/{id}` - Delete a specific job application
- `GET /applications/stats/` - Get your application statistics

## Usage Examples

### 1. Register a New User

```bash
curl -X POST "http://localhost:8000/register/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "jobseeker1",
       "password": "secure123",
       "email": "jobseeker1@example.com",
       "full_name": "John Doe"
     }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/login/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "jobseeker1",
       "password": "secure123"
     }'
```

### 3. Add a Job Application

```bash
curl -X POST "http://localhost:8000/applications/" \
     -H "Content-Type: application/json" \
     -u "jobseeker1:secure123" \
     -d '{
       "job_title": "Senior Software Engineer",
       "company": "Tech Corp",
       "date_applied": "2024-01-15T10:30:00",
       "status": "applied",
       "description": "Full-stack development role with Python and React",
       "salary_range": "$80,000 - $120,000",
       "location": "San Francisco, CA",
       "notes": "Applied through company website"
     }'
```

### 4. Get All Your Applications

```bash
curl -X GET "http://localhost:8000/applications/" \
     -u "jobseeker1:secure123"
```

### 5. Get Applications with Filters

```bash
# Filter by status
curl -X GET "http://localhost:8000/applications/?status_filter=applied" \
     -u "jobseeker1:secure123"

# Filter by company
curl -X GET "http://localhost:8000/applications/?company_filter=Tech" \
     -u "jobseeker1:secure123"

# Limit results
curl -X GET "http://localhost:8000/applications/?limit=5" \
     -u "jobseeker1:secure123"
```

### 6. Update an Application

```bash
curl -X PUT "http://localhost:8000/applications/1" \
     -H "Content-Type: application/json" \
     -u "jobseeker1:secure123" \
     -d '{
       "status": "interview_scheduled",
       "notes": "Phone interview scheduled for next Tuesday at 2 PM"
     }'
```

### 7. Delete an Application

```bash
curl -X DELETE "http://localhost:8000/applications/1" \
     -u "jobseeker1:secure123"
```

### 8. Get Application Statistics

```bash
curl -X GET "http://localhost:8000/applications/stats/" \
     -u "jobseeker1:secure123"
```

## Application Status Options

- `applied` - Application submitted
- `interview_scheduled` - Interview has been scheduled
- `interviewed` - Interview completed
- `offer_received` - Job offer received
- `rejected` - Application rejected
- `withdrawn` - Application withdrawn by user

## Security Features

- **Password Hashing**: All passwords are hashed with salt before storage
- **User Isolation**: Each user can only access their own applications
- **HTTP Basic Authentication**: Secure authentication for all protected endpoints
- **Input Validation**: Comprehensive validation of all input data
- **Error Handling**: Proper error responses without information leakage

## Data Files

- `users.json` - User accounts and authentication data
- `applications.json` - All job applications (filtered by user in API responses)

## Authentication

The API uses HTTP Basic Authentication. Include your username and password in requests:

```
Authorization: Basic <base64(username:password)>
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200` - Success
- `201` - Created successfully
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid credentials)
- `404` - Not Found (application doesn't exist or no permission)
- `500` - Internal Server Error

## Example Response Formats

### Application List Response
```json
{
  "applications": [
    {
      "id": 1,
      "job_title": "Senior Software Engineer",
      "company": "Tech Corp",
      "date_applied": "2024-01-15T10:30:00",
      "status": "applied",
      "username": "jobseeker1",
      "description": "Full-stack development role",
      "salary_range": "$80,000 - $120,000",
      "location": "San Francisco, CA",
      "notes": "Applied through company website"
    }
  ],
  "total_applications": 1,
  "username": "jobseeker1"
}
```

### Statistics Response
```json
{
  "username": "jobseeker1",
  "total_applications": 5,
  "status_breakdown": {
    "applied": 2,
    "interview_scheduled": 1,
    "interviewed": 1,
    "rejected": 1,
    "offer_received": 0,
    "withdrawn": 0
  },
  "companies_applied": ["Tech Corp", "StartupXYZ", "BigTech Inc"],
  "recent_applications": [...]
}
```

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
