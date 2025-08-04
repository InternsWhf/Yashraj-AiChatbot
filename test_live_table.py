#!/usr/bin/env python3
import requests
import json

def test_table_functionality():
    """Test table functionality in the live system"""
    print("🧪 Testing Live Table Functionality")
    print("=" * 50)
    
    # Test questions that should return tables
    test_questions = [
        "show me the setup instructions table",
        "what are the die numbers and cycle times", 
        "display the coil size data",
        "show me the table with die numbers",
        "what is the setup table information"
    ]
    
    for question in test_questions:
        print(f"\n🔍 Testing: {question}")
        
        try:
            response = requests.post(
                "http://localhost:8000/ask",
                json={"question": question},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "")
                source_files = data.get("source_files", [])
                has_context = data.get("has_context", False)
                
                print(f"✅ Response received ({len(answer)} characters)")
                print(f"📄 Sources: {source_files}")
                print(f"🔗 Has context: {has_context}")
                
                # Check if answer contains table formatting
                if "|" in answer and ("---" in answer or "|" in answer.split('\n')[1] if len(answer.split('\n')) > 1 else False):
                    print("🎉 TABLE DETECTED IN RESPONSE!")
                    print("=" * 30)
                    print(answer[:500] + "..." if len(answer) > 500 else answer)
                    print("=" * 30)
                    return True
                else:
                    print("❌ No table format detected in response")
                    print("Answer preview:", answer[:200] + "..." if len(answer) > 200 else answer)
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    return False

if __name__ == "__main__":
    success = test_table_functionality()
    if success:
        print("\n🎉 Table functionality is working!")
    else:
        print("\n⚠️ Table functionality needs improvement") 