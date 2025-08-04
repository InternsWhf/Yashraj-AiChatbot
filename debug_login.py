#!/usr/bin/env python3
"""
Debug Login Issue
================
Debug script to see exactly what's happening during login.
"""

import requests
import json
from backend.auth import verify_user_credentials, get_user_by_email

def debug_login():
    """Debug the login process step by step"""
    print("🔍 Debugging Login Process")
    print("=" * 40)
    
    # Test credentials
    email = "interns@whfpl.in"
    password = "Yashraj"
    
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
    print()
    
    # Step 1: Check if user exists
    print("1️⃣ Checking if user exists...")
    user = get_user_by_email(email)
    if user:
        print("✅ User found in database")
        print(f"   ID: {user['id']}")
        print(f"   Email: {user['email']}")
        print(f"   Name: {user['name']}")
        print(f"   Role: {user['role']}")
        print(f"   Password hash: {user['password_hash'][:20]}...")
    else:
        print("❌ User not found in database")
        return
    
    print()
    
    # Step 2: Test password verification
    print("2️⃣ Testing password verification...")
    verified_user = verify_user_credentials(email, password)
    if verified_user:
        print("✅ Password verification successful")
        print(f"   User ID: {verified_user['id']}")
        print(f"   User keys: {list(verified_user.keys())}")
    else:
        print("❌ Password verification failed")
        return
    
    print()
    
    # Step 3: Test API login
    print("3️⃣ Testing API login...")
    try:
        response = requests.post("http://localhost:8000/auth/login", json={
            "email": email,
            "password": password
        })
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API login successful")
            print(f"   Response keys: {list(data.keys())}")
            if 'user' in data:
                print(f"   User keys: {list(data['user'].keys())}")
        else:
            print("❌ API login failed")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API request error: {e}")

if __name__ == "__main__":
    debug_login() 