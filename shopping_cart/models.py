from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class UserRole(str, Enum):
    """User roles enumeration"""
    ADMIN = "admin"
    CUSTOMER = "customer"

class User(BaseModel):
    """User model with role-based access"""
    username: str
    password_hash: str
    role: UserRole
    email: Optional[str] = None

class UserRegistration(BaseModel):
    """Model for user registration"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    password: str = Field(..., min_length=6, description="Plain text password")
    role: UserRole = Field(default=UserRole.CUSTOMER, description="User role")
    email: Optional[str] = Field(None, description="User email")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure123",
                "role": "customer",
                "email": "john@example.com"
            }
        }

class LoginRequest(BaseModel):
    """Model for login request"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure123"
            }
        }

class LoginResponse(BaseModel):
    """Model for login response"""
    message: str
    username: str
    role: UserRole

class Product(BaseModel):
    """Product model"""
    id: int
    name: str
    description: str
    price: float
    stock: int
    category: str

class ProductCreate(BaseModel):
    """Model for creating a product"""
    name: str = Field(..., min_length=1, max_length=100, description="Product name")
    description: str = Field(..., max_length=500, description="Product description")
    price: float = Field(..., gt=0, description="Product price (must be positive)")
    stock: int = Field(..., ge=0, description="Stock quantity")
    category: str = Field(..., min_length=1, max_length=50, description="Product category")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Laptop",
                "description": "High-performance laptop for work and gaming",
                "price": 999.99,
                "stock": 10,
                "category": "Electronics"
            }
        }

class CartItem(BaseModel):
    """Cart item model"""
    product_id: int
    quantity: int = Field(..., gt=0, description="Quantity must be positive")

class CartAddRequest(BaseModel):
    """Model for adding items to cart"""
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity to add")
    
    class Config:
        schema_extra = {
            "example": {
                "product_id": 1,
                "quantity": 2
            }
        }

class CartResponse(BaseModel):
    """Model for cart response"""
    username: str
    items: List[dict]
    total_items: int
    total_price: float

class ProductResponse(BaseModel):
    """Model for product response"""
    products: List[Product]
    total_products: int