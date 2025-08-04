from backend.database import DocumentDatabase

# Test database operations
db = DocumentDatabase()

print("Testing database operations...")

# Test adding a document
try:
    result = db.add_document(
        filename="test_debug.txt",
        file_path="/uploads/test_debug.txt",
        file_size=100,
        file_type="txt",
        user_id="test_user"
    )
    print(f"Add document result: {result}")
except Exception as e:
    print(f"Error adding document: {e}")
    import traceback
    traceback.print_exc()

# Test getting documents
try:
    docs = db.get_documents()
    print(f"Documents in database: {len(docs)}")
    for doc in docs:
        print(f"  - {doc['filename']}")
except Exception as e:
    print(f"Error getting documents: {e}")
    import traceback
    traceback.print_exc() 