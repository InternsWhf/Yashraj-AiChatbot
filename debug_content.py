#!/usr/bin/env python3
"""
Debug script to see what content is stored in the database
"""

import sqlite3

def debug_database_content():
    """Check what's actually stored in the database"""
    print("🔍 Debugging Database Content")
    print("=" * 50)
    
    conn = sqlite3.connect("documents.db")
    cursor = conn.cursor()
    
    # Check documents table
    cursor.execute("SELECT * FROM documents")
    documents = cursor.fetchall()
    print(f"📄 Documents in database: {len(documents)}")
    for doc in documents:
        print(f"   - {doc[1]} (ID: {doc[0]}, Type: {doc[4]})")
    
    # Check chunks table
    cursor.execute("SELECT * FROM document_chunks LIMIT 5")
    chunks = cursor.fetchall()
    print(f"\n📝 Sample chunks in database: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} (ID: {chunk[0]}, Document ID: {chunk[1]}):")
        print(f"Content preview: {chunk[3][:200]}...")
    
    # Check total chunks
    cursor.execute("SELECT COUNT(*) FROM document_chunks")
    total_chunks = cursor.fetchone()[0]
    print(f"\n📊 Total chunks in database: {total_chunks}")
    
    conn.close()

if __name__ == "__main__":
    debug_database_content() 