#!/usr/bin/env python3
"""
Test Login Functionality
=======================
Test script to verify the login system is working correctly.
"""

import requests
import json
import time

def test_login():
    """Test the login functionality"""
    print("🧪 Testing Login Functionality")
    print("=" * 40)
    
    # Wait for backend to be ready
    print("⏳ Waiting for backend to be ready...")
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend is ready!")
                break
        except:
            pass
        time.sleep(1)
        print(f"⏳ Attempt {i+1}/10...")
    else:
        print("❌ Backend not responding")
        return False
    
    # Test login
    login_data = {
        "email": "interns@whfpl.in",
        "password": "Yashraj"
    }
    
    print(f"\n🔐 Testing login with: {login_data['email']}")
    
    try:
        response = requests.post(
            "http://localhost:8000/auth/login",
            json=login_data,
            timeout=10
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Login successful!")
            print(f"🔑 Token received: {data.get('access_token', 'N/A')[:20]}...")
            print(f"👤 User ID: {data.get('user', {}).get('user_id', 'N/A')}")
            print(f"📧 Email: {data.get('user', {}).get('email', 'N/A')}")
            print(f"👨‍💼 Name: {data.get('user', {}).get('name', 'N/A')}")
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        return False

if __name__ == "__main__":
    success = test_login()
    if success:
        print("\n🎉 Login functionality is working correctly!")
    else:
        print("\n⚠️ Login functionality needs attention") 