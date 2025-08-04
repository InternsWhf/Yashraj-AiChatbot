# backend/qa_engine.py

import os
import asyncio
from openai import OpenAI
from dotenv import load_dotenv
import fitz  # PyMuPDF
import pandas as pd
from PIL import Image
import pytesseract
import tempfile
import json
import sqlite3
from datetime import datetime

load_dotenv()

# Initialize OpenAI client (optional)
try:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    openai_available = True
except:
    openai_available = False
    client = None

class QAEngine:
    def __init__(self):
        self.client = client
        self.openai_available = openai_available
        self.db_path = "documents.db"
        self.init_database()
    
    def init_database(self):
        """Initialize database for document storage"""
        # Use the existing database structure from database.py
        pass
    
    def store_chunks(self, filename, chunks, file_type, user_id=None):
        """Store document chunks in database using existing structure"""
        from .database import DocumentDatabase
        
        try:
            # Use the proper database manager
            db = DocumentDatabase()
            
            # Add document to database
            document_id = db.add_document(
                filename=filename,
                file_path=f"/uploads/{filename}",
                file_size=len(str(chunks)),
                file_type=file_type,
                user_id=user_id
            )
            
            if document_id:
                # Add chunks to database
                db.add_chunks(document_id, chunks)
                print(f"Successfully stored {len(chunks)} chunks for {filename} (document_id: {document_id})")
                return True
            else:
                print(f"Failed to add document {filename} to database")
                return False
                
        except Exception as e:
            print(f"Error storing chunks: {e}")
            return False
    
    def get_all_chunks(self, user_id=None):
        """Get all document chunks from database using existing structure"""
        import sqlite3
        
        try:
            # Direct database query to get all chunks for specific user
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # First check if tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents'")
            if not cursor.fetchone():
                print("Documents table does not exist")
                conn.close()
                return []
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='document_chunks'")
            if not cursor.fetchone():
                print("Document_chunks table does not exist")
                conn.close()
                return []
            
            if user_id:
                cursor.execute('''
                    SELECT d.filename, dc.content, d.file_type 
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    WHERE d.user_id = ?
                    ORDER BY d.upload_time DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT d.filename, dc.content, d.file_type 
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    ORDER BY d.upload_time DESC
                ''')
            
            chunks = cursor.fetchall()
            print(f"Retrieved {len(chunks)} chunks from database for user: {user_id}")
            conn.close()
            return chunks
        except Exception as e:
            print(f"Error getting chunks: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def extract_text_from_pdf(self, file_path):
        """Extract text and tables from PDF file with enhanced processing"""
        try:
            doc = fitz.open(file_path)
            text = ""
            tables = []
            
            for page_num, page in enumerate(doc):
                # Get text with better formatting
                page_text = page.get_text("text")
                
                # Add page number for reference
                text += f"\n--- Page {page_num + 1} ---\n"
                text += page_text
                text += "\n"
                
                # Extract tables from the page
                page_tables = self.extract_tables_from_page(page, page_num + 1)
                tables.extend(page_tables)
            
            doc.close()
            
            # Clean up the text
            text = text.replace('\x00', '')  # Remove null characters
            text = ' '.join(text.split())  # Normalize whitespace
            
            # Add table markers to text
            for i, table in enumerate(tables):
                table_marker = f"\n\n[TABLE_{i+1}]\n{table['title']}\n{table['data']}\n[/TABLE_{i+1}]\n\n"
                text += table_marker
            
            print(f"Extracted {len(text)} characters and {len(tables)} tables from PDF")
            return text
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def extract_tables_from_page(self, page, page_num):
        """Extract tables from a PDF page"""
        tables = []
        try:
            # Get table blocks from the page
            blocks = page.get_text("dict")
            
            for block in blocks["blocks"]:
                if "lines" in block:
                    # Check if this looks like a table (multiple lines with similar structure)
                    lines = block["lines"]
                    if len(lines) > 2:  # Potential table
                        table_data = []
                        headers = []
                        
                        for line in lines:
                            row = []
                            for span in line["spans"]:
                                row.append(span["text"].strip())
                            if row:
                                table_data.append(row)
                        
                        # Check if this looks like a table (consistent column structure)
                        if len(table_data) > 2 and self.is_table_structure(table_data):
                            # Try to identify headers
                            if table_data:
                                headers = table_data[0]
                                data_rows = table_data[1:]
                                
                                table = {
                                    'title': f'Table from Page {page_num}',
                                    'headers': headers,
                                    'data': data_rows,
                                    'page': page_num
                                }
                                tables.append(table)
                                print(f"Found table on page {page_num} with {len(data_rows)} rows")
        
        except Exception as e:
            print(f"Error extracting tables from page {page_num}: {e}")
        
        return tables
    
    def is_table_structure(self, data):
        """Check if data looks like a table structure"""
        if len(data) < 2:
            return False
        
        # Check if rows have similar number of columns
        first_row_cols = len(data[0])
        for row in data[1:]:
            if len(row) != first_row_cols:
                return False
        
        # Check if there are numbers or structured data
        has_numbers = False
        for row in data:
            for cell in row:
                if any(char.isdigit() for char in cell):
                    has_numbers = True
                    break
        
        return has_numbers or first_row_cols > 2
    
    def extract_text_from_excel(self, file_path):
        """Extract text and tables from Excel file with comprehensive processing"""
        try:
            # Read all sheets in the Excel file
            excel_file = pd.ExcelFile(file_path)
            text = f"EXCEL FILE: {file_path}\n"
            text += f"Total Sheets: {len(excel_file.sheet_names)}\n"
            text += f"Sheets: {', '.join(excel_file.sheet_names)}\n\n"
            
            tables = []
            
            for sheet_name in excel_file.sheet_names:
                try:
                    # Read sheet with different engines if needed
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
                    except:
                        try:
                            df = pd.read_excel(file_path, sheet_name=sheet_name, engine='xlrd')
                        except:
                            df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    text += f"\n--- Sheet: {sheet_name} ---\n"
                    text += f"Rows: {len(df)}, Columns: {len(df.columns)}\n"
                    
                    # Handle different types of Excel content
                    if len(df.columns) > 0 and len(df) > 0:
                        # Check if this looks like a data table
                        if len(df.columns) > 1:
                            # Extract as structured table
                            table_data = {
                                'title': f'Data Table from Sheet: {sheet_name}',
                                'headers': df.columns.tolist(),
                                'data': df.values.tolist(),
                                'sheet': sheet_name
                            }
                            tables.append(table_data)
                            
                            # Add comprehensive table representation
                            table_marker = f"\n\n[TABLE_{len(tables)}]\n{table_data['title']}\n"
                            table_marker += " | ".join([str(h) for h in table_data['headers']]) + "\n"
                            
                            # Add data rows (limit to first 100 rows for readability)
                            for i, row in enumerate(table_data['data'][:100]):
                                row_str = " | ".join([str(cell) if pd.notna(cell) else "" for cell in row])
                                table_marker += f"{row_str}\n"
                            
                            if len(table_data['data']) > 100:
                                table_marker += f"... (showing first 100 of {len(table_data['data'])} rows)\n"
                            
                            table_marker += f"[/TABLE_{len(tables)}]\n\n"
                            text += table_marker
                            
                            print(f"Processed table in sheet '{sheet_name}' with {len(df)} rows and {len(df.columns)} columns")
                        else:
                            # Single column data
                            text += f"Single Column Data:\n"
                            for index, value in df.iloc[:, 0].items():
                                if pd.notna(value):
                                    text += f"Row {index + 1}: {value}\n"
                    else:
                        text += "Empty sheet or no data found.\n"
                    
                    # Add column information
                    if len(df.columns) > 0:
                        text += f"Columns: {', '.join([str(col) for col in df.columns])}\n"
                    
                    text += "\n"
                    
                except Exception as sheet_error:
                    print(f"Error processing sheet '{sheet_name}': {sheet_error}")
                    text += f"Error processing sheet '{sheet_name}': {str(sheet_error)}\n\n"
            
            print(f"Successfully extracted {len(text)} characters and {len(tables)} tables from Excel file")
            return text
            
        except Exception as e:
            print(f"Error extracting text from Excel file {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return f"EXCEL FILE: {file_path}\nError processing Excel file: {str(e)}\nPlease ensure the file is not corrupted and is a valid Excel format."
    
    def extract_text_from_image(self, file_path):
        """Extract text from image using OCR with enhanced processing"""
        try:
            image = Image.open(file_path)
            # Enhanced OCR with multiple configurations
            text = pytesseract.image_to_string(image, config='--psm 6 --oem 3')
            
            # If no text found, try different OCR modes
            if not text.strip():
                text = pytesseract.image_to_string(image, config='--psm 3 --oem 3')
            
            return f"IMAGE CONTENT: {text}\nSource: {file_path}"
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return f"IMAGE FILE: {file_path} (OCR processing failed)"

    def extract_text_from_csv(self, file_path):
        """Extract data from CSV file with table formatting"""
        try:
            df = pd.read_csv(file_path)
            text = f"CSV DATA TABLE:\n{df.to_string(index=False)}\n"
            text += f"Columns: {list(df.columns)}\n"
            text += f"Rows: {len(df)}\n"
            text += f"Data types: {df.dtypes.to_dict()}\n"
            return text
        except Exception as e:
            print(f"Error extracting text from CSV: {e}")
            return f"CSV FILE: {file_path} (processing failed)"

    def extract_text_from_word(self, file_path):
        """Extract text from Word documents"""
        try:
            # For now, return a placeholder - would need python-docx for full implementation
            return f"WORD DOCUMENT: {file_path}\nContent extraction requires additional processing."
        except Exception as e:
            print(f"Error extracting text from Word document: {e}")
            return f"WORD FILE: {file_path} (processing failed)"

    def extract_text_from_powerpoint(self, file_path):
        """Extract text from PowerPoint presentations"""
        try:
            # For now, return a placeholder - would need python-pptx for full implementation
            return f"POWERPOINT PRESENTATION: {file_path}\nContent extraction requires additional processing."
        except Exception as e:
            print(f"Error extracting text from PowerPoint: {e}")
            return f"POWERPOINT FILE: {file_path} (processing failed)"

    def extract_text_from_txt(self, file_path):
        """Extract text from plain text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            return f"TEXT DOCUMENT:\n{text}\nSource: {file_path}"
        except Exception as e:
            print(f"Error extracting text from text file: {e}")
            return f"TEXT FILE: {file_path} (processing failed)"
    
    def chunk_text(self, text, chunk_size=1000, overlap=200):
        """Split text into overlapping chunks with better context preservation"""
        chunks = []
        
        # Split by sentences first to preserve context
        import re
        sentences = re.split(r'[.!?]+', text)
        
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # If adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - overlap)
                current_chunk = current_chunk[overlap_start:] + " " + sentence
            else:
                current_chunk += " " + sentence
        
        # Add the last chunk if it has content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Ensure minimum chunk size and remove empty chunks
        final_chunks = []
        for chunk in chunks:
            if len(chunk) > 50:  # Minimum meaningful chunk size
                final_chunks.append(chunk)
        
        print(f"Created {len(final_chunks)} chunks from text")
        return final_chunks

    def chunk_text_enhanced(self, text, filename, file_type, chunk_size=1000, overlap=200):
        """Enhanced chunking with metadata and better structure preservation"""
        chunks = []
        
        if not text or len(text) <= chunk_size:
            if text:
                chunk = f"FILE: {filename}\nTYPE: {file_type}\nCONTENT:\n{text}"
                chunks.append(chunk)
            return chunks
        
        # Split into sections first (for better context)
        sections = text.split('\n\n')
        
        for section in sections:
            if len(section) <= chunk_size:
                if section.strip():
                    chunk = f"FILE: {filename}\nTYPE: {file_type}\nSECTION:\n{section.strip()}"
                    chunks.append(chunk)
            else:
                # Further split large sections
                section_chunks = self.chunk_text(section, chunk_size, overlap)
                for i, chunk_text in enumerate(section_chunks):
                    if chunk_text.strip():
                        chunk = f"FILE: {filename}\nTYPE: {file_type}\nSECTION_PART: {i+1}\n{chunk_text.strip()}"
                        chunks.append(chunk)
        
        return chunks
    
    def search_chunks(self, question, top_k=50, user_id=None):
        """Enhanced search across all uploaded documents"""
        question_lower = question.lower()
        relevant_chunks = []
        
        # Get all chunks from database
        all_chunks = self.get_all_chunks(user_id)
        print(f"Searching across {len(all_chunks)} chunks from database for user: {user_id}")
        
        # If no chunks found, return empty list
        if not all_chunks:
            print("No chunks found in database")
            return []
        
        # For document listing requests, return a sample from each document
        if any(keyword in question_lower for keyword in ['list', 'all documents', 'uploaded', 'files', 'documents']):
            print("Document listing request detected - optimizing search")
            # Group chunks by filename and return one chunk per document
            document_chunks = {}
            for chunk_data in all_chunks:
                if isinstance(chunk_data, dict):
                    filename = chunk_data['filename']
                else:
                    filename = chunk_data[0]
                
                if filename not in document_chunks:
                    document_chunks[filename] = chunk_data
            
            # Return one chunk per document
            result_chunks = list(document_chunks.values())
            print(f"Returning {len(result_chunks)} documents for listing")
            return result_chunks
        
        # Define important keywords for WHF operations
        whf_keywords = {
            'hammer': ['hammer', '2t', '3t', '1t', 'ton', 'forging', 'strike', 'drop', 'cdf'],
            'steps': ['step', 'method', 'procedure', 'process', 'operation', 'instruction', 'work instruction'],
            'safety': ['safety', 'ppe', 'protective', 'helmet', 'gloves', 'emergency', 'danger'],
            'equipment': ['equipment', 'die', 'tool', 'furnace', 'heating', 'press', 'machine'],
            'quality': ['quality', 'inspection', 'check', 'verify', 'standard', 'test'],
            'temperature': ['temperature', 'heat', 'heating', 'furnace', 'celsius', 'fahrenheit'],
            'pressure': ['pressure', 'psi', 'bar', 'force', 'load'],
            'time': ['time', 'duration', 'minutes', 'hours', 'seconds'],
            'general': ['work', 'instruction', 'document', 'scope', 'master', 'copy']
        }
        
        for chunk_data in all_chunks:
            # Handle both tuple and dict formats
            if isinstance(chunk_data, dict):
                content = chunk_data['content']
                filename = chunk_data['filename']
                file_type = 'pdf'  # Default type
            else:
                filename, content, file_type = chunk_data
            content_lower = content.lower()
            score = 0
            
            # Simple word matching - this is what we need
            question_words = question_lower.split()
            
            # Check each word in the question
            for word in question_words:
                if len(word) > 2:  # Only meaningful words
                    if word in content_lower:
                        score += 10  # High score for exact matches
                        print(f"Found word '{word}' in {filename}")
            
            # Check for partial matches (for compound words like "work instruction")
            for word in question_words:
                if len(word) > 4:
                    for content_word in content_lower.split():
                        if word in content_word or content_word in word:
                            score += 5
                            print(f"Found partial match '{word}' in {filename}")
            
            # If we found any matches, add this chunk
            if score > 0:
                relevant_chunks.append({
                    'content': content,
                    'filename': filename,
                    'file_type': file_type,
                    'score': score
                })
                print(f"Added {filename} with score {score}")
        
        # Sort by relevance score and return top results
        relevant_chunks.sort(key=lambda x: x['score'], reverse=True)
        
        # Return ALL relevant chunks (no limit) or top_k if specified
        if top_k and top_k > 0:
            result_chunks = relevant_chunks[:top_k]
        else:
            result_chunks = relevant_chunks
        
        print(f"Returning {len(result_chunks)} relevant chunks out of {len(all_chunks)} total chunks")
        return result_chunks
    
    def get_answer_from_context(self, question, context):
        """Get answer using OpenAI if available, otherwise use rule-based responses"""
        if self.openai_available and self.client:
            try:
                # Check if context contains tables
                has_tables = "[TABLE_" in context
                
                if has_tables:
                    prompt = f"""
You are an AI assistant for Western Heat & Forge (WHF), a manufacturing company specializing in forging operations.

IMPORTANT INSTRUCTIONS:
1. Use information from ALL documents provided in the context
2. Be comprehensive and thorough in your response
3. If the context contains tables (marked with [TABLE_X] and [/TABLE_X]), format them as proper tables in your response using markdown table syntax
4. Reference specific documents when providing information
5. Ensure you cover all relevant information from all available documents

Example table format:
| Column1 | Column2 | Column3 |
|---------|---------|---------|
| Data1   | Data2   | Data3   |
| Data4   | Data5   | Data6   |

Context from multiple documents:
{context}

Question: {question}

Answer comprehensively using information from ALL relevant documents:"""
                else:
                    prompt = f"""
You are an AI assistant for Western Heat & Forge (WHF), a manufacturing company specializing in forging operations.

IMPORTANT INSTRUCTIONS:
1. Use information from ALL documents provided in the context
2. Be comprehensive and thorough in your response
3. Reference specific documents when providing information
4. Ensure you cover all relevant information from all available documents
5. If summarizing multiple documents, provide a complete overview

Context from multiple documents:
{context}

Question: {question}

Answer comprehensively using information from ALL relevant documents:"""
                
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI error: {e}")
                # Fall back to rule-based responses
        
        # Rule-based responses for WHF operations
        return self.get_rule_based_answer(question)
    
    def get_rule_based_answer(self, question):
        """Provide rule-based answers for WHF operations"""
        question_lower = question.lower()
        
        # WHF Company Information
        if "company" in question_lower or "whf" in question_lower or "western heat" in question_lower:
            return """**Western Heat & Forge (WHF) Company Information:**

**About WHF:**
- Specialized manufacturing company in forging operations
- Produces high-quality forged components for various industries
- Located in India with state-of-the-art manufacturing facilities

**Core Services:**
- Hot forging operations
- Die forging and impression die forging
- Custom forged components
- Heat treatment services
- Quality control and testing

**Equipment:**
- 2T & 3T Hammers for forging operations
- Induction heating furnaces
- Heat treatment furnaces
- Quality control equipment

**Quality Standards:**
- ISO 9001:2015 certified
- AS9100 aerospace quality management
- NADCAP certified for special processes
- Customer-specific quality requirements"""
        
        # Hammer Operations
        elif "hammer" in question_lower or "2t" in question_lower or "3t" in question_lower:
            if "1st step" in question_lower or "first step" in question_lower:
                return """**1st Step for 2T & 3T Hammer Operation:**

**Safety Preparation:**
1. **PPE Check** - Wear proper Personal Protective Equipment
   - Safety helmet, safety glasses, ear protection
   - Heat-resistant gloves and safety shoes
   - Flame-resistant clothing

2. **Work Area Inspection:**
   - Ensure work area is clean and clear of obstacles
   - Check emergency stop buttons are functional
   - Verify all safety guards are in place
   - Clear access to emergency exits

3. **Equipment Pre-Start Check:**
   - Inspect hammer dies for damage or wear
   - Check hydraulic system pressure and oil levels
   - Verify control panel functions and displays
   - Test emergency systems and alarms

4. **Material Preparation:**
   - Verify billet dimensions and quality
   - Check material specifications and grade
   - Ensure proper heating temperature (1100-1200°C)
   - Confirm billet is free from defects

**Reference:** WI-PR-06 Work Instruction for 2T & 3T Hammer operations"""
            
            elif "step" in question_lower:
                return """**2T & 3T Hammer Work Instructions - Complete Process:**

**Step 1: Safety & Equipment Check**
- PPE inspection and work area preparation
- Equipment pre-start checks and safety systems

**Step 2: Material Preparation**
- Billet heating to 1100-1200°C
- Material verification and quality check

**Step 3: Die Setup & Alignment**
- Die installation and proper alignment
- Lubrication application and clearance checks

**Step 4: Forging Operation**
- Controlled striking with proper force monitoring
- Temperature maintenance during operation

**Step 5: Quality Control**
- Inspection of forged parts
- Dimensional and visual quality checks

**Key Parameters:**
- Temperature Range: 1100-1200°C
- Safety: Always follow lockout/tagout procedures
- Documentation: Refer to WI-PR-06 for complete procedures"""
            
            else:
                return """**2T & 3T Hammer Operations:**

**Equipment Overview:**
- 2T Hammer: 2-ton capacity forging hammer
- 3T Hammer: 3-ton capacity forging hammer
- Used for impression die forging operations

**Typical Applications:**
- Aerospace components
- Automotive parts
- Industrial machinery components
- Custom forged parts

**Process Steps:**
1. Safety preparation and equipment check
2. Material heating and preparation
3. Die setup and alignment
4. Forging operation with controlled striking
5. Quality inspection and documentation

**Safety Requirements:**
- Proper PPE (helmet, glasses, gloves, safety shoes)
- Emergency stop system functional
- Safety guards in place
- Lockout/tagout procedures followed

**Quality Standards:**
- Dimensional accuracy per specifications
- Surface finish requirements
- Material integrity verification
- Documentation of process parameters"""
        
        # Heating Operations
        elif "heat" in question_lower or "furnace" in question_lower or "heating" in question_lower:
            return """**Heating Operations for Forging:**

**Standard Heating Process:**
1. **Pre-heating Phase**
   - Furnace startup and temperature stabilization
   - Load distribution planning and spacing

2. **Loading Operations**
   - Proper billet placement and spacing
   - Temperature zone optimization

3. **Temperature Control**
   - Maintain 1100-1200°C range for most steels
   - Monitor temperature uniformity
   - Control heating rate to prevent thermal shock

4. **Time Management**
   - Follow specified heating duration
   - Monitor soak time for uniform heating

5. **Quality Verification**
   - Check uniform heating before forging
   - Verify temperature distribution
   - Inspect for surface defects

**Key Parameters:**
- **Temperature Range:** 1100-1200°C (typical)
- **Heating Rate:** 100-200°C per hour (depending on material)
- **Soak Time:** 30-60 minutes at forging temperature
- **Uniformity:** ±10°C across billet cross-section

**Equipment Types:**
- Induction heating furnaces
- Gas-fired furnaces
- Electric resistance furnaces
- Continuous pusher furnaces

**Safety Considerations:**
- Proper ventilation and exhaust
- Temperature monitoring systems
- Emergency shutdown procedures
- Personal protective equipment"""
        
        # General Forging Questions
        elif "forging" in question_lower or "forge" in question_lower:
            return """**Forging Operations at WHF:**

**Types of Forging:**
1. **Impression Die Forging**
   - Uses dies to shape metal
   - High precision and repeatability
   - Used for complex geometries

2. **Open Die Forging**
   - Free-form shaping
   - Used for simple shapes
   - Good for large components

**Process Steps:**
1. **Material Selection** - Choose appropriate alloy and grade
2. **Heating** - Heat to forging temperature (1100-1200°C)
3. **Forging** - Shape using hammers or presses
4. **Heat Treatment** - Improve mechanical properties
5. **Quality Control** - Inspect dimensions and properties

**Quality Standards:**
- Dimensional accuracy: ±0.5mm typical
- Surface finish: Ra 3.2 or better
- Mechanical properties: Per material specifications
- Documentation: Complete process records

**Applications:**
- Aerospace components
- Automotive parts
- Industrial machinery
- Oil and gas equipment
- Defense applications"""
        
        # Default response
        else:
            return f"""I understand you're asking about: **{question}**

This appears to be related to WHF's manufacturing operations. For specific technical details, please:

1. **Ask about specific equipment** (e.g., "hammer", "furnace", "press")
2. **Mention specific steps** (e.g., "1st step", "2nd step", "safety")
3. **Specify the process** (e.g., "heating", "forging", "quality control")

I can provide detailed information about:
- **2T & 3T Hammer operations**
- **Heating and furnace processes**
- **Forging procedures**
- **Quality control standards**
- **Safety requirements**
- **Company information**

Please ask a more specific question about WHF's operations."""
    
    async def process_file(self, file_path, filename, user_id=None):
        """Process uploaded file and extract ALL content (text, tables, images, data)"""
        try:
            file_extension = filename.split(".")[-1].lower()
            print(f"Processing file: {filename} ({file_extension})")
            
            # Extract content based on file type with comprehensive processing
            if file_extension == "pdf":
                text = self.extract_text_from_pdf(file_path)
            elif file_extension in ["xlsx", "xls"]:
                text = self.extract_text_from_excel(file_path)
            elif file_extension in ["png", "jpg", "jpeg"]:
                text = self.extract_text_from_image(file_path)
            elif file_extension == "csv":
                text = self.extract_text_from_csv(file_path)
            elif file_extension in ["doc", "docx"]:
                text = self.extract_text_from_word(file_path)
            elif file_extension in ["ppt", "pptx"]:
                text = self.extract_text_from_powerpoint(file_path)
            elif file_extension == "txt":
                text = self.extract_text_from_txt(file_path)
            else:
                print(f"Unsupported file type: {file_extension}")
                return False
            
            if text and text.strip():
                print(f"Extracted {len(text)} characters from {filename}")
                
                # Create comprehensive chunks with metadata
                chunks = self.chunk_text_enhanced(text, filename, file_extension)
                
                if chunks:
                    # Store chunks in database with user association
                    success = self.store_chunks(filename, chunks, file_extension, user_id)
                    
                    if success:
                        print(f"Successfully processed {filename}: {len(chunks)} chunks stored in database")
                        return True
                    else:
                        print(f"Failed to store chunks for {filename}")
                        return False
                else:
                    print(f"No chunks created from {filename}")
                    return False
            else:
                print(f"No content extracted from {filename}")
                return False
            
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def get_answer(self, question, chat_context="", user_id=None):
        """Get answer with context from all uploaded documents"""
        try:
            # Check if this is a document listing request
            question_lower = question.lower()
            if any(keyword in question_lower for keyword in ['list', 'all documents', 'uploaded', 'files', 'documents']):
                # For document listing, get ALL chunks without limit
                relevant_chunks = self.search_chunks(question, top_k=None, user_id=user_id)
            else:
                # For regular questions, use increased limit
                relevant_chunks = self.search_chunks(question, top_k=100, user_id=user_id)
            
            if relevant_chunks:
                # Combine chunks into context with better organization
                context_parts = []
                source_files = []
                file_contents = {}
                
                # Group content by filename for better organization
                for chunk_data in relevant_chunks:
                    filename = chunk_data['filename']
                    content = chunk_data['content']
                    
                    if filename not in file_contents:
                        file_contents[filename] = []
                        source_files.append(filename)
                    
                    file_contents[filename].append(content)
                
                # Create organized context with file headers
                for filename, contents in file_contents.items():
                    context_parts.append(f"\n=== DOCUMENT: {filename} ===\n")
                    context_parts.extend(contents)
                    context_parts.append(f"\n=== END: {filename} ===\n")
                
                context = "\n\n".join(context_parts)
                
                # Use AI to generate answer from context
                if self.openai_available and self.client:
                    answer = self.get_answer_from_context(question, context)
                else:
                    # Fallback to rule-based with context
                    answer = f"""Based on your uploaded documents, here's what I found:

**Context from documents:**
{context[:800]}...

**Answer:**
{self.get_rule_based_answer(question)}

*Note: This answer combines information from your uploaded documents with general WHF knowledge.*"""
                
                return answer, source_files, True
            else:
                # No relevant documents found, use rule-based response
                answer = self.get_rule_based_answer(question)
                return answer, [], False
            
        except Exception as e:
            print(f"Error getting answer: {e}")
            import traceback
            traceback.print_exc()
            return f"Sorry, I couldn't process your question right now. Error: {str(e)}. Please try again.", [], False

# Create global instance
qa_engine = QAEngine()
