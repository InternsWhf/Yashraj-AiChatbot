#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('documents.db')
cursor = conn.cursor()

# Check the actual data
cursor.execute('''
    SELECT d.filename, dc.content, d.file_type 
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    LIMIT 3
''')

rows = cursor.fetchall()
print(f"Found {len(rows)} rows")

for i, row in enumerate(rows):
    print(f"\nRow {i+1}:")
    print(f"Filename: {row[0]}")
    print(f"Content preview: {row[1][:100]}...")
    print(f"File type: {row[2]}")

conn.close() 