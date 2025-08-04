#!/usr/bin/env python3
"""
Reset Authentication Database
============================
This script resets the user database and creates a test user for the WHF AI Chatbot.
"""

import os
import sqlite3
import bcrypt
import uuid

def reset_database():
    """Reset the user database and create a test user"""
    print("🔄 Resetting user database...")
    
    # Remove existing database
    if os.path.exists('users.db'):
        os.remove('users.db')
        print("✅ Removed existing database")
    
    # Create new database
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table
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
    
    # Create test user
    test_email = "interns@whfpl.in"
    test_password = "Yashraj"
    test_name = "WHF Intern"
    
    # Hash password properly
    password_hash = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Insert test user
    user_id = str(uuid.uuid4())
    cursor.execute('''
        INSERT INTO users (id, email, password_hash, name, role)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, test_email, password_hash, test_name, 'standard'))
    
    conn.commit()
    conn.close()
    
    print("✅ Database reset complete!")
    print("📧 Test user created:")
    print(f"   Email: {test_email}")
    print(f"   Password: {test_password}")
    print(f"   Name: {test_name}")
    print()
    print("🔐 You can now login with these credentials!")

if __name__ == "__main__":
    reset_database() 