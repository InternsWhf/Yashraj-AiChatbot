#!/usr/bin/env python3
"""
Test script to verify document processing functionality
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_document_processing():
    """Test the document processing system"""
    print("🧪 Testing WHF AI Chatbot Document Processing")
    print("=" * 50)
    
    try:
        # Import the QA engine
        from backend.qa_engine import qa_engine
        print("✅ QA Engine imported successfully")
        
        # Test database connection
        from backend.database import DocumentDatabase
        db = DocumentDatabase()
        print("✅ Database connection successful")
        
        # Check if we have any existing documents
        existing_chunks = db.get_all_chunks()
        print(f"📊 Found {len(existing_chunks)} existing chunks in database")
        
        # Test text extraction functions
        print("\n🔍 Testing text extraction functions...")
        
        # Test PDF processing (if any PDF files exist)
        pdf_files = list(Path("data/uploads").glob("*.pdf"))
        if pdf_files:
            test_pdf = str(pdf_files[0])
            print(f"📄 Testing PDF extraction: {test_pdf}")
            
            text = qa_engine.extract_text_from_pdf(test_pdf)
            if text.strip():
                print(f"✅ PDF extraction successful: {len(text)} characters")
                chunks = qa_engine.chunk_text(text)
                print(f"✅ Text chunking successful: {len(chunks)} chunks")
            else:
                print("❌ PDF extraction failed - no text extracted")
        
        # Test Excel processing (if any Excel files exist)
        excel_files = list(Path("data/uploads").glob("*.xlsx")) + list(Path("data/uploads").glob("*.xls"))
        if excel_files:
            test_excel = str(excel_files[0])
            print(f"📊 Testing Excel extraction: {test_excel}")
            
            text = qa_engine.extract_text_from_excel(test_excel)
            if text.strip():
                print(f"✅ Excel extraction successful: {len(text)} characters")
                chunks = qa_engine.chunk_text(text)
                print(f"✅ Text chunking successful: {len(chunks)} chunks")
            else:
                print("❌ Excel extraction failed - no text extracted")
        
        # Test search functionality
        print("\n🔍 Testing search functionality...")
        test_question = "hammer operation steps"
        relevant_chunks = qa_engine.search_chunks(test_question, top_k=5)
        print(f"✅ Search successful: Found {len(relevant_chunks)} relevant chunks")
        
        # Test answer generation
        print("\n🤖 Testing answer generation...")
        answer, source_files, has_context = await qa_engine.get_answer(test_question)
        print(f"✅ Answer generation successful: {len(answer)} characters")
        print(f"📁 Source files: {source_files}")
        print(f"🔗 Has context: {has_context}")
        
        print("\n🎉 All tests completed successfully!")
        print("=" * 50)
        print("📝 Summary:")
        print(f"   - Database chunks: {len(existing_chunks)}")
        print(f"   - Search results: {len(relevant_chunks)}")
        print(f"   - Answer length: {len(answer)} characters")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_document_processing()) 