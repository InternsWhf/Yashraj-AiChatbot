#!/usr/bin/env python3
import sys
sys.path.append('.')

from backend.qa_engine import qa_engine

# Test search
print("Testing search...")
chunks = qa_engine.search_chunks("hammer", 5)
print(f"Found {len(chunks)} chunks for 'hammer'")

if chunks:
    print("First chunk content:")
    print(chunks[0]['content'][:200])
else:
    print("No chunks found!") 