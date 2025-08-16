# KodeCampTask6 - FastAPI Security & Authentication Projects

A comprehensive collection of FastAPI applications demonstrating various authentication methods, security patterns, and API design principles.

## 📋 Project Overview

This repository contains four distinct FastAPI applications, each showcasing different authentication and security approaches:

1. **Secure Student Portal** - HTTP Basic Authentication with grade management
2. **Shopping Cart API** - Role-based access control with admin/customer roles
3. **Job Application Tracker** - User-specific data access with dependency injection
4. **Notes API** - JWT Bearer token authentication with secure note management

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd KodeCampTask6
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running Individual APIs

Each API can be run independently from its respective directory:

```bash
# Student Portal
cd secure_student_portal
uvicorn main:app --reload --port 8001

# Shopping Cart
cd shopping_cart
uvicorn main:app --reload --port 8002

# Job Tracker
cd job_tracker
uvicorn main:app --reload --port 8003

# Notes API
cd notes_api
uvicorn main:app --reload --port 8004
```

## 📚 API Documentation

Each API includes interactive documentation available at `/docs` endpoint when running.

## 🔐 Authentication Methods Demonstrated

### 1. HTTP Basic Authentication
**Used in:** Secure Student Portal
- Username/password sent with each request
- Server-side password hashing with salt
- Simple but effective for internal APIs

### 2. Role-Based Access Control (RBAC)
**Used in:** Shopping Cart API
- User roles: Admin, Customer
- Different permissions per role
- Dependency injection for role checking

### 3. User-Specific Data Access
**Used in:** Job Application Tracker
- Each user sees only their own data
- Dependency injection for user filtering
- Complete data isolation

### 4. JWT Bearer Token Authentication
**Used in:** Notes API
- Stateless token-based authentication
- Configurable token expiration
- Industry-standard JWT implementation

---

## 🎓 1. Secure Student Portal

**Directory:** `secure_student_portal/`  
**Authentication:** HTTP Basic Auth  
**Port:** 8001

### Features
- Student registration with grade management
- HTTP Basic Authentication
- Password hashing with salt
- Grade viewing for authenticated students

### Key Endpoints
- `POST /register/` - Register new student
- `POST /login/` - Authenticate student
- `GET /grades/` - View grades (requires auth)

### Usage Example
```bash
# Register student
curl -X POST "http://localhost:8001/register/" \
     -H "Content-Type: application/json" \
     -d '{"username": "student1", "password": "pass123", "grades": [85.5, 92.0]}'

# View grades (with Basic Auth)
curl -X GET "http://localhost:8001/grades/" \
     -u "student1:pass123"
```

---

## 🛒 2. Shopping Cart API

**Directory:** `shopping_cart/`  
**Authentication:** HTTP Basic Auth + Role-Based Access  
**Port:** 8002

### Features
- User registration with roles (admin/customer)
- Product management (admin only)
- Shopping cart functionality (authenticated users)
- Role-based endpoint protection

### Key Endpoints
- `POST /register/` - Register user with role
- `POST /login/` - User authentication
- `GET /products/` - Browse products (public)
- `POST /admin/add_product/` - Add product (admin only)
- `POST /cart/add/` - Add to cart (authenticated)
- `GET /cart/` - View cart (authenticated)

### Default Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** `admin`

### Usage Example
```bash
# Register customer
curl -X POST "http://localhost:8002/register/" \
     -H "Content-Type: application/json" \
     -d '{"username": "customer1", "password": "pass123", "role": "customer"}'

# Add product (admin only)
curl -X POST "http://localhost:8002/admin/add_product/" \
     -H "Content-Type: application/json" \
     -u "admin:admin123" \
     -d '{"name": "Laptop", "price": 999.99, "stock": 10, "category": "Electronics"}'

# Add to cart
curl -X POST "http://localhost:8002/cart/add/" \
     -H "Content-Type: application/json" \
     -u "customer1:pass123" \
     -d '{"product_id": 1, "quantity": 2}'
```

---

## 💼 3. Job Application Tracker

**Directory:** `job_tracker/`  
**Authentication:** HTTP Basic Auth + User Isolation  
**Port:** 8003

### Features
- Secure job application management
- User-specific data access (complete isolation)
- Full CRUD operations for applications
- Application statistics and filtering

### Key Endpoints
- `POST /register/` - Register user
- `POST /login/` - User authentication
- `POST /applications/` - Add job application
- `GET /applications/` - View own applications (with filters)
- `PUT /applications/{id}` - Update application
- `DELETE /applications/{id}` - Delete application
- `GET /applications/stats/` - Application statistics

### Usage Example
```bash
# Register user
curl -X POST "http://localhost:8003/register/" \
     -H "Content-Type: application/json" \
     -d '{"username": "jobseeker1", "password": "pass123", "email": "job@example.com"}'

# Add job application
curl -X POST "http://localhost:8003/applications/" \
     -H "Content-Type: application/json" \
     -u "jobseeker1:pass123" \
     -d '{
       "job_title": "Software Engineer",
       "company": "Tech Corp",
       "date_applied": "2024-01-15T10:30:00",
       "status": "applied"
     }'

# View applications
curl -X GET "http://localhost:8003/applications/" \
     -u "jobseeker1:pass123"
```

---

## 📝 4. Notes API with JWT Authentication

**Directory:** `notes_api/`  
**Authentication:** JWT Bearer Tokens  
**Port:** 8004

### Features
- JWT token-based authentication
- Secure note management
- Token expiration (30 minutes)
- Search and filtering capabilities

### Key Endpoints
- `POST /register/` - Register user
- `POST /login/` - Login (returns JWT token)
- `POST /notes/` - Add note (requires token)
- `GET /notes/` - View notes (requires token)
- `PUT /notes/{id}` - Update note (requires token)
- `DELETE /notes/{id}` - Delete note (requires token)

### Usage Example
```bash
# Register user
curl -X POST "http://localhost:8004/register/" \
     -H "Content-Type: application/json" \
     -d '{"username": "noteuser", "password": "pass123"}'

# Login and get JWT token
curl -X POST "http://localhost:8004/login/" \
     -H "Content-Type: application/json" \
     -d '{"username": "noteuser", "password": "pass123"}'

# Response: {"access_token": "eyJ...", "token_type": "bearer", ...}

# Add note with JWT token
curl -X POST "http://localhost:8004/notes/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -d '{"title": "Meeting Notes", "content": "Important meeting details..."}'

# Get notes
curl -X GET "http://localhost:8004/notes/" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---



## 📁 Project Structure

```
KodeCampTask6/
├── README.md                    # This file
├── requirements.txt             # Global dependencies
├── .gitignore                   # Git ignore rules
├── secure_student_portal/       # HTTP Basic Auth + Grades
│   ├── main.py
│   ├── models.py
│   ├── README.md
│   └── test_api.py
├── shopping_cart/               # Role-Based Access Control
│   ├── main.py
│   ├── models.py
│   ├── auth.py
│   ├── README.md
│   └── test_api.py
├── job_tracker/                 # User-Specific Data Access
│   ├── main.py
│   ├── models.py
│   ├── auth.py
│   ├── README.md
│   └── test_api.py
└── notes_api/                   # JWT Bearer Token Auth
    ├── main.py
    ├── models.py
    ├── auth.py
    ├── README.md
    └── test_api.py
```

## 🔒 Security Features Implemented

### Password Security
- **Salted Hashing**: All passwords hashed with salt
- **Secure Storage**: No plain text passwords stored
- **Validation**: Minimum password requirements

### Authentication Security
- **Multiple Methods**: Basic Auth, Role-based, JWT tokens
- **Token Expiration**: JWT tokens expire automatically
- **User Isolation**: Complete data separation between users
- **Role Validation**: Proper role-based access control

### API Security
- **Input Validation**: Comprehensive validation with Pydantic
- **Error Handling**: Secure error responses
- **Logging**: Security event logging
- **CORS Ready**: Configurable for frontend integration

## 🛠️ Technologies Used

- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and serialization
- **Python-JOSE**: JWT token handling
- **Uvicorn**: ASGI server
- **JSON**: Data persistence (production should use databases)

## 📖 Learning Objectives Achieved

1. **HTTP Basic Authentication** implementation
2. **Role-Based Access Control** (RBAC) patterns
3. **JWT Token Authentication** with Bearer tokens
4. **User Data Isolation** techniques
5. **Dependency Injection** for security
6. **Password Hashing** and security best practices
7. **API Design** patterns and RESTful principles
8. **Error Handling** and security considerations



## 📝 API Documentation

Each API provides interactive documentation:
- **Swagger UI**: Available at `/docs` endpoint
- **ReDoc**: Available at `/redoc` endpoint
- **OpenAPI Schema**: Available at `/openapi.json`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 🎯 Summary

This project demonstrates four different approaches to API security and authentication:

1. **Basic Authentication** - Simple but effective
2. **Role-Based Access** - Scalable permission system
3. **User Data Isolation** - Complete data separation
4. **JWT Tokens** - Modern, stateless authentication

Each approach has its use cases and trade-offs, providing a comprehensive understanding of API security patterns in modern web development.

---

**Happy Coding! 🚀**