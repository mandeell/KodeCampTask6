# Shopping Cart API

A FastAPI application for shopping with role-based access control.

## Features

- **User Management**: Registration and authentication with role-based access (admin/customer)
- **Product Management**: Admins can add products, all users can browse
- **Shopping Cart**: Authenticated users can add items to their cart
- **Data Persistence**: Products stored in `products.json`, cart data in `cart.json`, users in `users.json`
- **Role-Based Access Control**: Different permissions for admins and customers

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

## Default Admin Account

- **Username**: `admin`
- **Password**: `admin123`
- **Role**: `admin`

## API Endpoints

### Public Endpoints

- `GET /` - API information and endpoints
- `GET /products/` - Browse all products (no authentication required)
- `POST /register/` - Register a new user
- `POST /login/` - User authentication

### Admin Only Endpoints

- `POST /admin/add_product/` - Add new products (requires admin role)

### Authenticated User Endpoints

- `POST /cart/add/` - Add items to cart (requires authentication)
- `GET /cart/` - View user's cart (requires authentication)

## Usage Examples

### 1. Register a New Customer

```bash
curl -X POST "http://localhost:8000/register/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "customer1",
       "password": "password123",
       "role": "customer",
       "email": "customer1@example.com"
     }'
```

### 2. Register a New Admin

```bash
curl -X POST "http://localhost:8000/register/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin2",
       "password": "adminpass123",
       "role": "admin",
       "email": "admin2@example.com"
     }'
```

### 3. Login

```bash
curl -X POST "http://localhost:8000/login/" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "customer1",
       "password": "password123"
     }'
```

### 4. Browse Products (Public)

```bash
curl -X GET "http://localhost:8000/products/"
```

### 5. Add Product (Admin Only)

```bash
curl -X POST "http://localhost:8000/admin/add_product/" \
     -H "Content-Type: application/json" \
     -u "admin:admin123" \
     -d '{
       "name": "Gaming Mouse",
       "description": "High-precision gaming mouse",
       "price": 79.99,
       "stock": 15,
       "category": "Electronics"
     }'
```

### 6. Add Item to Cart (Authenticated Users)

```bash
curl -X POST "http://localhost:8000/cart/add/" \
     -H "Content-Type: application/json" \
     -u "customer1:password123" \
     -d '{
       "product_id": 1,
       "quantity": 2
     }'
```

### 7. View Cart (Authenticated Users)

```bash
curl -X GET "http://localhost:8000/cart/" \
     -u "customer1:password123"
```

## Authentication

The API uses HTTP Basic Authentication. Include your username and password in the request headers:

```
Authorization: Basic <base64(username:password)>
```

## Role-Based Access Control

- **Admin**: Can add products and access all customer features
- **Customer**: Can browse products, add items to cart, and manage their own cart
- **Public**: Can browse products and register/login

## Data Files

- `users.json` - User accounts and authentication data
- `products.json` - Product catalog
- `cart.json` - User shopping carts

## Error Handling

The API includes comprehensive error handling with appropriate HTTP status codes:

- `400` - Bad Request (validation errors, insufficient stock, etc.)
- `401` - Unauthorized (invalid credentials)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (product not found)
- `500` - Internal Server Error (server-side errors)

## Security Features

- Password hashing with salt
- Role-based access control
- Input validation
- Comprehensive logging
- Error handling without information leakage