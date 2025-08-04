#!/usr/bin/env python3
import sys
sys.path.append('.')

from backend.qa_engine import qa_engine

# Check what chunks we're getting
print("Getting chunks from database...")
chunks = qa_engine.get_all_chunks()
print(f"Got {len(chunks)} chunks from database")

if chunks:
    print("First chunk:")
    filename, content, file_type = chunks[0]
    print(f"File: {filename}")
    print(f"Content preview: {content[:100]}...")
    print(f"Type: {file_type}")
    
    # Test simple search
    print("\nTesting simple search...")
    if "hammer" in content.lower():
        print("Found 'hammer' in content!")
    else:
        print("'hammer' NOT found in content")
else:
    print("No chunks returned from database!") 