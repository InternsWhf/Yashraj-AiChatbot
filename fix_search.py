#!/usr/bin/env python3
import sqlite3

# Direct database query to get all chunks
conn = sqlite3.connect('documents.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT d.filename, dc.content, d.file_type 
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    ORDER BY d.upload_time DESC
''')

all_chunks = cursor.fetchall()
print(f"Found {len(all_chunks)} chunks in database")

# Test search for "hammer"
question = "hammer"
question_lower = question.lower()
relevant_chunks = []

for filename, content, file_type in all_chunks:
    content_lower = content.lower()
    score = 0
    
    # Simple word matching
    if question in content_lower:
        score += 10
        print(f"Found 'hammer' in {filename}")
    
    if score > 0:
        relevant_chunks.append({
            'content': content,
            'filename': filename,
            'file_type': file_type,
            'score': score
        })

print(f"\nFound {len(relevant_chunks)} relevant chunks for 'hammer'")

if relevant_chunks:
    print("\nFirst relevant chunk:")
    chunk = relevant_chunks[0]
    print(f"File: {chunk['filename']}")
    print(f"Content: {chunk['content'][:200]}...")

conn.close() 