from fastapi import FastAPI, HTTPException, Depends, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import uvicorn
from datetime import datetime, timedelta
import jwt
import hashlib
import sqlite3
import os

# Create database if it doesn't exist
def init_db():
    conn = sqlite3.connect('voicebot.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            phone_number TEXT,
            hashed_password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

app = FastAPI(title="ComplaintHub API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    full_name: str
    phone_number: Optional[str] = None
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: int
    email: str
    full_name: str
    phone_number: Optional[str] = None
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(email: str):
    conn = sqlite3.connect('voicebot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id: int):
    conn = sqlite3.connect('voicebot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "id": user[0],
        "email": user[1],
        "full_name": user[3],  # full_name is at index 3
        "phone_number": user[4],  # phone_number is at index 4
        "role": "user"  # default role
    }

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "ComplaintHub API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/auth/signup", response_model=dict)
def signup(user_data: UserCreate):
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Insert new user
    conn = sqlite3.connect('voicebot.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (email, full_name, phone_number, hashed_password) VALUES (?, ?, ?, ?)",
        (user_data.email, user_data.full_name, user_data.phone_number, hashed_password)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"message": "User created successfully", "user_id": user_id}

@app.post("/api/v1/login/access-token", response_model=Token)
def login(username: str = Form(...), password: str = Form(...)):
    # Get user from database
    user = get_user_by_email(username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Debug: Print user data structure
    print(f"User data: {user}")
    print(f"User length: {len(user)}")
    print(f"Password provided: {password}")
    print(f"Stored hash: {user[4] if len(user) > 4 else 'N/A'}")
    print(f"Generated hash: {hash_password(password)}")
    
    # Verify password - The password hash is at index 2 based on the actual database structure
    if not verify_password(password, user[2]):  # hashed_password is at index 2
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user[0])}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/users/me", response_model=User)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user

@app.get("/api/v1/test")
def test_endpoint():
    return {"message": "API is working!", "path": "/api/v1/test"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 