from fastapi import FastAPI, HTTPException, status, Depends
from models import (
    UserRegistration, LoginRequest, LoginResponse, ProductCreate, Product,
    CartAddRequest, CartResponse, ProductResponse, User, UserRole
)
from auth import (
    authenticate_user, get_current_user, require_admin, require_authenticated_user,
    create_default_admin, register_user, hash_password, load_users
)
import json
import os
import logging
from typing import List

app = FastAPI(
    title="Shopping Cart API",
    description="A FastAPI application for shopping with role-based access control",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRODUCTS_FILE = "products.json"
CART_FILE = "cart.json"

# Initialize default admin on startup
@app.on_event("startup")
async def startup_event():
    """Initialize default admin user and sample data"""
    create_default_admin()
    initialize_sample_products()

def load_products():
    """Load products from JSON file with proper error handling"""
    try:
        if os.path.exists(PRODUCTS_FILE):
            with open(PRODUCTS_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        return []
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading products file: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error loading products file: {e}")
        return []

def save_products(products_list):
    """Save products to JSON file with proper error handling"""
    try:
        with open(PRODUCTS_FILE, "w") as f:
            json.dump(products_list, f, indent=2)
    except IOError as e:
        logger.error(f"Error saving products file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save product data")
    except Exception as e:
        logger.error(f"Unexpected error saving products file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save product data")

def load_cart():
    """Load cart data from JSON file with proper error handling"""
    try:
        if os.path.exists(CART_FILE):
            with open(CART_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        return {}
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading cart file: {e}")
        return {}
    except Exception as e:
        logger.error(f"Unexpected error loading cart file: {e}")
        return {}

def save_cart(cart_dict):
    """Save cart data to JSON file with proper error handling"""
    try:
        with open(CART_FILE, "w") as f:
            json.dump(cart_dict, f, indent=2)
    except IOError as e:
        logger.error(f"Error saving cart file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save cart data")
    except Exception as e:
        logger.error(f"Unexpected error saving cart file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save cart data")

def get_next_product_id():
    """Get the next available product ID"""
    products = load_products()
    if not products:
        return 1
    return max(product["id"] for product in products) + 1

def find_product_by_id(product_id: int):
    """Find a product by its ID"""
    products = load_products()
    for product in products:
        if product["id"] == product_id:
            return product
    return None

def initialize_sample_products():
    """Initialize sample products if none exist"""
    products = load_products()
    if not products:
        sample_products = [
            {
                "id": 1,
                "name": "Laptop",
                "description": "High-performance laptop for work and gaming",
                "price": 999.99,
                "stock": 10,
                "category": "Electronics"
            },
            {
                "id": 2,
                "name": "Smartphone",
                "description": "Latest smartphone with advanced features",
                "price": 699.99,
                "stock": 25,
                "category": "Electronics"
            },
            {
                "id": 3,
                "name": "Coffee Mug",
                "description": "Ceramic coffee mug with custom design",
                "price": 12.99,
                "stock": 50,
                "category": "Home & Kitchen"
            }
        ]
        save_products(sample_products)
        logger.info("Sample products initialized")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Shopping Cart API",
        "version": "1.0.0",
        "endpoints": {
            "register": "POST /register/",
            "login": "POST /login/",
            "products": "GET /products/",
            "add_product": "POST /admin/add_product/ (admin only)",
            "add_to_cart": "POST /cart/add/ (authenticated users)",
            "view_cart": "GET /cart/ (authenticated users)"
        },
        "default_admin": {
            "username": "admin",
            "password": "admin123",
            "note": "Change this password in production!"
        }
    }

@app.post('/register/', status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegistration):
    """Register a new user"""
    try:
        result = register_user(
            username=user_data.username,
            password=user_data.password,
            role=user_data.role,
            email=user_data.email
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
            role=UserRole(user_data["role"])
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )

@app.post('/admin/add_product/', status_code=status.HTTP_201_CREATED)
async def add_product(product_data: ProductCreate, admin_user: User = Depends(require_admin)):
    """Add a new product (admin only)"""
    try:
        products = load_products()
        
        # Check if product with same name already exists
        for product in products:
            if product["name"].lower() == product_data.name.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Product with this name already exists"
                )
        
        # Create new product
        new_product = {
            "id": get_next_product_id(),
            "name": product_data.name,
            "description": product_data.description,
            "price": product_data.price,
            "stock": product_data.stock,
            "category": product_data.category
        }
        
        products.append(new_product)
        save_products(products)
        
        logger.info(f"Product '{product_data.name}' added by admin {admin_user.username}")
        
        return {
            "message": "Product added successfully",
            "product": new_product
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add product due to server error"
        )

@app.get('/products/', response_model=ProductResponse)
async def get_products():
    """Get all products (public endpoint)"""
    try:
        products = load_products()
        
        return ProductResponse(
            products=[Product(**product) for product in products],
            total_products=len(products)
        )
    
    except Exception as e:
        logger.error(f"Error retrieving products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products due to server error"
        )

@app.post('/cart/add/', status_code=status.HTTP_201_CREATED)
async def add_to_cart(cart_item: CartAddRequest, user: User = Depends(require_authenticated_user)):
    """Add item to cart (authenticated users only)"""
    try:
        # Check if product exists
        product = find_product_by_id(cart_item.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Check stock availability
        if product["stock"] < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {product['stock']}"
            )
        
        # Load cart data
        cart_data = load_cart()
        
        # Initialize user cart if it doesn't exist
        if user.username not in cart_data:
            cart_data[user.username] = []
        
        user_cart = cart_data[user.username]
        
        # Check if item already in cart
        item_found = False
        for item in user_cart:
            if item["product_id"] == cart_item.product_id:
                # Update quantity
                new_quantity = item["quantity"] + cart_item.quantity
                if product["stock"] < new_quantity:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Insufficient stock. Available: {product['stock']}, requested total: {new_quantity}"
                    )
                item["quantity"] = new_quantity
                item_found = True
                break
        
        if not item_found:
            # Add new item to cart
            user_cart.append({
                "product_id": cart_item.product_id,
                "product_name": product["name"],
                "price": product["price"],
                "quantity": cart_item.quantity
            })
        
        # Save cart
        save_cart(cart_data)
        
        logger.info(f"User {user.username} added {cart_item.quantity} of product {cart_item.product_id} to cart")
        
        return {
            "message": "Item added to cart successfully",
            "product_name": product["name"],
            "quantity": cart_item.quantity
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart due to server error"
        )

@app.get('/cart/', response_model=CartResponse)
async def get_cart(user: User = Depends(require_authenticated_user)):
    """Get user's cart (authenticated users only)"""
    try:
        cart_data = load_cart()
        user_cart = cart_data.get(user.username, [])
        
        total_items = sum(item["quantity"] for item in user_cart)
        total_price = sum(item["price"] * item["quantity"] for item in user_cart)
        
        return CartResponse(
            username=user.username,
            items=user_cart,
            total_items=total_items,
            total_price=round(total_price, 2)
        )
    
    except Exception as e:
        logger.error(f"Error retrieving cart for {user.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart due to server error"
        )