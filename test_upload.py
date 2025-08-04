import requests
import json

# Test login
login_data = {
    "email": "interns@whfpl.in",
    "password": "Yashraj"
}

response = requests.post("http://localhost:8000/auth/login", json=login_data)
print("Login response:", response.status_code)
print("Login response:", response.json())

if response.status_code == 200:
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test upload endpoint
    print("\nTesting upload endpoint...")
    
    # Create a simple test file
    test_content = "This is a test document for WHF AI Assistant."
    
    files = {
        'file': ('test.txt', test_content, 'text/plain')
    }
    
    upload_response = requests.post("http://localhost:8000/upload", headers=headers, files=files)
    print("Upload response status:", upload_response.status_code)
    print("Upload response:", upload_response.text)
    
    # Test documents endpoint
    docs_response = requests.get("http://localhost:8000/documents", headers=headers)
    print("\nDocuments response status:", docs_response.status_code)
    print("Documents response:", docs_response.json())
else:
    print("Login failed!") 