#!/usr/bin/env python3
import sys
sys.path.append('.')

from backend.qa_engine import qa_engine
import asyncio

async def test_table_extraction():
    """Test table extraction from documents"""
    print("🧪 Testing Table Extraction from Documents")
    print("=" * 50)
    
    # Test PDF table extraction
    pdf_files = list(Path("data/uploads").glob("*.pdf"))
    if pdf_files:
        test_pdf = str(pdf_files[0])
        print(f"📄 Testing PDF table extraction: {test_pdf}")
        
        text = qa_engine.extract_text_from_pdf(test_pdf)
        if "[TABLE_" in text:
            print("✅ Found tables in PDF!")
            # Extract table sections
            import re
            table_sections = re.findall(r'\[TABLE_\d+\](.*?)\[/TABLE_\d+\]', text, re.DOTALL)
            print(f"Found {len(table_sections)} table sections")
            
            for i, table in enumerate(table_sections):
                print(f"\nTable {i+1}:")
                print(table[:200] + "..." if len(table) > 200 else table)
        else:
            print("❌ No tables found in PDF")
    
    # Test Excel table extraction
    excel_files = list(Path("data/uploads").glob("*.xlsx")) + list(Path("data/uploads").glob("*.xls"))
    if excel_files:
        test_excel = str(excel_files[0])
        print(f"\n📊 Testing Excel table extraction: {test_excel}")
        
        text = qa_engine.extract_text_from_excel(test_excel)
        if "[TABLE_" in text:
            print("✅ Found tables in Excel!")
            # Extract table sections
            import re
            table_sections = re.findall(r'\[TABLE_\d+\](.*?)\[/TABLE_\d+\]', text, re.DOTALL)
            print(f"Found {len(table_sections)} table sections")
            
            for i, table in enumerate(table_sections):
                print(f"\nTable {i+1}:")
                print(table[:200] + "..." if len(table) > 200 else table)
        else:
            print("❌ No tables found in Excel")
    
    # Test search for table-related questions
    print("\n🔍 Testing table search...")
    test_questions = [
        "show me the setup instructions table",
        "what are the die numbers and cycle times",
        "display the coil size data"
    ]
    
    for question in test_questions:
        print(f"\nQuestion: {question}")
        chunks = qa_engine.search_chunks(question, 3)
        print(f"Found {len(chunks)} relevant chunks")
        
        if chunks:
            # Check if any chunks contain tables
            table_chunks = [chunk for chunk in chunks if "[TABLE_" in chunk['content']]
            print(f"Found {len(table_chunks)} chunks with tables")
            
            if table_chunks:
                print("✅ Table search is working!")
                break
    
    print("\n🎉 Table extraction test completed!")

if __name__ == "__main__":
    from pathlib import Path
    asyncio.run(test_table_extraction()) 