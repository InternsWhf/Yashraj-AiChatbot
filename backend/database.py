import sqlite3
import json
import os
from datetime import datetime

class DocumentDatabase:
    def __init__(self, db_path="documents.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if user_id column exists
        cursor.execute("PRAGMA table_info(documents)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            # Add user_id column to existing table
            try:
                cursor.execute('ALTER TABLE documents ADD COLUMN user_id TEXT')
                print("Added user_id column to documents table")
            except Exception as e:
                print(f"Error adding user_id column: {e}")
        
        # Create documents table (if it doesn't exist)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_type TEXT,
                user_id TEXT,
                UNIQUE(filename)
            )
        ''')
        
        # Create document chunks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_id INTEGER,
                content TEXT NOT NULL,
                chunk_size INTEGER,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        # Create chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                source_files TEXT,
                timestamp TEXT NOT NULL,
                has_context BOOLEAN DEFAULT 0,
                response_time REAL DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_document(self, filename, file_path, file_size, file_type, user_id=None):
        """Add a new document to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO documents (filename, file_path, file_size, file_type, upload_time, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (filename, file_path, file_size, file_type, datetime.now(), user_id))
            
            document_id = cursor.lastrowid
            conn.commit()
            return document_id
        except Exception as e:
            print(f"Error adding document: {e}")
            return None
        finally:
            conn.close()
    
    def add_chunks(self, document_id, chunks):
        """Add document chunks to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            for i, chunk in enumerate(chunks):
                cursor.execute('''
                    INSERT INTO document_chunks (document_id, chunk_id, content, chunk_size)
                    VALUES (?, ?, ?, ?)
                ''', (document_id, i, chunk, len(chunk)))
            
            conn.commit()
        except Exception as e:
            print(f"Error adding chunks: {e}")
        finally:
            conn.close()
    
    def get_all_chunks(self):
        """Get all document chunks for searching"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT dc.content, d.filename, dc.chunk_id
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                ORDER BY d.upload_time DESC, dc.chunk_id
            ''')
            
            chunks = []
            for row in cursor.fetchall():
                chunks.append({
                    "content": row[0],
                    "filename": row[1],
                    "chunk_id": row[2]
                })
            
            return chunks
        except Exception as e:
            print(f"Error getting chunks: {e}")
            return []
        finally:
            conn.close()
    
    def store_chat_history(self, chat_entry):
        """Store chat history entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO chat_history (user_id, question, answer, source_files, timestamp, has_context, response_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                chat_entry["user_id"],
                chat_entry["question"],
                chat_entry["answer"],
                json.dumps(chat_entry["source_files"]),
                chat_entry["timestamp"],
                chat_entry["has_context"],
                chat_entry["response_time"]
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error storing chat history: {e}")
            return False
        finally:
            conn.close()
    
    def get_chat_history(self, user_id, limit=50, offset=0):
        """Get user's chat history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT question, answer, source_files, timestamp, has_context, response_time
                FROM chat_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            ''', (user_id, limit, offset))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    "question": row[0],
                    "answer": row[1],
                    "source_files": json.loads(row[2]) if row[2] else [],
                    "timestamp": row[3],
                    "has_context": row[4],
                    "response_time": row[5]
                })
            
            return history
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []
        finally:
            conn.close()
    
    def clear_chat_history(self, user_id):
        """Clear user's chat history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing chat history: {e}")
            return False
        finally:
            conn.close()

    def init_chat_sessions_tables(self):
        """Initialize chat sessions tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Create chat_sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT,
                    created_at TEXT,
                    last_updated TEXT,
                    message_count INTEGER DEFAULT 0
                )
            ''')
            
            # Create chat_messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
                )
            ''')
            
            conn.commit()
        except Exception as e:
            print(f"Error initializing chat sessions tables: {e}")
        finally:
            conn.close()

    def get_chat_sessions(self, user_id):
        """Get all chat sessions for a user"""
        self.init_chat_sessions_tables()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, title, created_at, last_updated, message_count
                FROM chat_sessions
                WHERE user_id = ?
                ORDER BY last_updated DESC
            ''', (user_id,))
            
            sessions = []
            for row in cursor.fetchall():
                session_id, title, created_at, last_updated, message_count = row
                
                # Get messages for this session
                cursor.execute('''
                    SELECT role, content, timestamp
                    FROM chat_messages
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                ''', (session_id,))
                
                messages = []
                for msg_row in cursor.fetchall():
                    messages.append({
                        "role": msg_row[0],
                        "content": msg_row[1],
                        "timestamp": msg_row[2]
                    })
                
                sessions.append({
                    "session_id": session_id,
                    "title": title or "New Chat",
                    "created_at": created_at,
                    "last_updated": last_updated,
                    "message_count": message_count,
                    "messages": messages
                })
            
            return sessions
        except Exception as e:
            print(f"Error getting chat sessions: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            conn.close()

    def save_chat_session(self, session_id, user_id, title, messages):
        """Save or update a chat session"""
        self.init_chat_sessions_tables()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if session exists
            cursor.execute('SELECT id FROM chat_sessions WHERE id = ?', (session_id,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing session
                cursor.execute('''
                    UPDATE chat_sessions 
                    SET title = ?, last_updated = ?, message_count = ?
                    WHERE id = ?
                ''', (title, datetime.now().isoformat(), len(messages), session_id))
            else:
                # Create new session
                cursor.execute('''
                    INSERT INTO chat_sessions (id, user_id, title, created_at, last_updated, message_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session_id, user_id, title, datetime.now().isoformat(), datetime.now().isoformat(), len(messages)))
            
            # Clear existing messages for this session
            cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
            
            # Insert all messages
            for msg in messages:
                cursor.execute('''
                    INSERT INTO chat_messages (session_id, role, content, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, msg["role"], msg["content"], msg.get("timestamp", datetime.now().isoformat())))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving chat session: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            conn.close()

    def delete_chat_session(self, session_id, user_id):
        """Delete a chat session and its messages"""
        self.init_chat_sessions_tables()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Delete messages first
            cursor.execute('DELETE FROM chat_messages WHERE session_id = ?', (session_id,))
            # Delete session
            cursor.execute('DELETE FROM chat_sessions WHERE id = ? AND user_id = ?', (session_id, user_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting chat session: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_stats(self, user_id):
        """Get user's analytics statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get document count
            cursor.execute('SELECT COUNT(*) FROM documents WHERE user_id = ?', (user_id,))
            doc_count = cursor.fetchone()[0]
            
            # Get chat count
            cursor.execute('SELECT COUNT(*) FROM chat_history WHERE user_id = ?', (user_id,))
            chat_count = cursor.fetchone()[0]
            
            # Get successful answers count
            cursor.execute('SELECT COUNT(*) FROM chat_history WHERE user_id = ? AND has_context = 1', (user_id,))
            success_count = cursor.fetchone()[0]
            
            # Get average response time
            cursor.execute('SELECT AVG(response_time) FROM chat_history WHERE user_id = ?', (user_id,))
            avg_response = cursor.fetchone()[0] or 0
            
            return {
                "total_documents": doc_count,
                "total_chats": chat_count,
                "successful_answers": success_count,
                "success_rate": (success_count / chat_count * 100) if chat_count > 0 else 0,
                "avg_response_time": round(avg_response, 2)
            }
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {
                "total_documents": 0,
                "total_chats": 0,
                "successful_answers": 0,
                "success_rate": 0,
                "avg_response_time": 0
            }
        finally:
            conn.close()
    
    def get_documents(self, user_id=None):
        """Get list of all uploaded documents (optionally filtered by user)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if user_id:
                cursor.execute('''
                    SELECT filename, file_size, file_type, upload_time
                    FROM documents
                    WHERE user_id = ?
                    ORDER BY upload_time DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT filename, file_size, file_type, upload_time
                    FROM documents
                    ORDER BY upload_time DESC
                ''')
            
            documents = []
            for row in cursor.fetchall():
                documents.append({
                    "filename": row[0],
                    "file_size": row[1],
                    "file_type": row[2],
                    "upload_time": row[3]
                })
            
            print(f"Retrieved {len(documents)} documents for user: {user_id}")
            return documents
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
        finally:
            conn.close()
    
    def delete_document(self, filename):
        """Delete a document and its chunks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get document ID
            cursor.execute('SELECT id FROM documents WHERE filename = ?', (filename,))
            result = cursor.fetchone()
            
            if result:
                document_id = result[0]
                
                # Delete chunks first
                cursor.execute('DELETE FROM document_chunks WHERE document_id = ?', (document_id,))
                
                # Delete document
                cursor.execute('DELETE FROM documents WHERE id = ?', (document_id,))
                
                conn.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
        finally:
            conn.close()
    
    def clear_all(self):
        """Clear all documents and chunks"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM document_chunks')
            cursor.execute('DELETE FROM documents')
            conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False
        finally:
            conn.close()

# Global database instance
db = DocumentDatabase()

class DatabaseManager:
    def __init__(self):
        self.db = db
    
    def get_documents(self, user_id=None):
        """Get list of uploaded documents (optionally filtered by user)"""
        return self.db.get_documents(user_id)
    
    def clear_documents(self, user_id=None):
        """Clear documents (optionally filtered by user)"""
        return self.db.clear_all()
    
    def delete_document(self, filename, user_id):
        """Delete a specific document"""
        return self.db.delete_document(filename)
    
    def store_document(self, filename, size, user_id):
        """Store document information"""
        file_type = filename.split(".")[-1].lower() if "." in filename else "unknown"
        return self.db.add_document(filename, f"/uploads/{filename}", size, file_type, user_id)
    
    def get_all_chunks(self):
        """Get all document chunks for searching"""
        return self.db.get_all_chunks() 
    
    def store_chat_history(self, chat_entry):
        """Store chat history entry"""
        return self.db.store_chat_history(chat_entry)
    
    def get_chat_history(self, user_id, limit=50, offset=0):
        """Get user's chat history"""
        return self.db.get_chat_history(user_id, limit, offset)
    
    def get_chat_sessions(self, user_id):
        """Get user's chat sessions"""
        return self.db.get_chat_sessions(user_id)
    
    def save_chat_session(self, session_id, user_id, title, messages):
        """Save a chat session"""
        return self.db.save_chat_session(session_id, user_id, title, messages)
    
    def delete_chat_session(self, session_id, user_id):
        """Delete a chat session"""
        return self.db.delete_chat_session(session_id, user_id)
    
    def clear_chat_history(self, user_id):
        """Clear user's chat history"""
        return self.db.clear_chat_history(user_id)
    
    def get_user_stats(self, user_id):
        """Get user's analytics statistics"""
        return self.db.get_user_stats(user_id) 