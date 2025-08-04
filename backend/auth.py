from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import os
from typing import Optional
import json
import bcrypt
import sqlite3
import uuid

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class AuthManager:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

auth_manager = AuthManager()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = auth_manager.verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return user_id

def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None

# User roles
class UserRole:
    ADMIN = "admin"
    STANDARD = "standard"

# SQLite Database for User Management
def init_user_db():
    """Initialize the SQLite database for user management"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'standard',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("User database initialized")

def get_user_by_email(email: str):
    """Get user by email from SQLite database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'email': user[1],
            'password_hash': user[2],
            'name': user[3],
            'role': user[4],
            'created_at': user[5],
            'last_login': user[6]
        }
    return None

def create_user(email: str, password: str, name: str, role: str = UserRole.STANDARD):
    """Create a new user in SQLite database"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return None
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create user
    user_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO users (id, email, password_hash, name, role)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, email, password_hash, name, role))
    
    conn.commit()
    conn.close()
    
    return user_id

def verify_user_credentials(email: str, password: str):
    """Verify user credentials and return user data if valid"""
    user = get_user_by_email(email)
    if not user:
        return None
    
    try:
        # Verify password - handle both string and bytes formats
        password_bytes = password.encode('utf-8')
        stored_hash = user['password_hash']
        
        # If stored hash is already bytes, use it directly
        if isinstance(stored_hash, bytes):
            hash_bytes = stored_hash
        else:
            # If stored hash is string, encode it
            hash_bytes = stored_hash.encode('utf-8')
        
        if bcrypt.checkpw(password_bytes, hash_bytes):
            # Update last login
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE email = ?', (email,))
            conn.commit()
            conn.close()
            return user
    except Exception as e:
        print(f"Password verification error: {e}")
        return None
    
    return None

# Initialize database on import
init_user_db() 