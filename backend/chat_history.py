from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import os
from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection - Made optional
chat_history_collection = None
client = None

# Only try to connect if MongoDB is explicitly configured
mongodb_uri = os.getenv("MONGODB_URI")
if mongodb_uri:
try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
        # Test connection
        client.admin.command('ping')
    db = client["whf_chatbot"]
    chat_history_collection = db["chat_history"]
    print("✅ Connected to MongoDB")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    chat_history_collection = None
    client = None
else:
    print("ℹ️ MongoDB not configured - using file-based chat history")

class ChatHistoryManager:
    def __init__(self):
        self.collection = chat_history_collection
    
    def store_chat(self, user_id: str, question: str, answer: str, 
                   source_files: List[str] = None, metadata: Dict[str, Any] = None):
        """Store a chat interaction"""
        if not self.collection:
            return None
        
        chat_entry = {
            "user_id": user_id,
            "question": question,
            "answer": answer,
            "source_files": source_files or [],
            "metadata": metadata or {},
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        try:
            result = self.collection.insert_one(chat_entry)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error storing chat: {e}")
            return None
    
    def get_user_history(self, user_id: str, limit: int = 50, offset: int = 0):
        """Get chat history for a specific user"""
        if not self.collection:
            return []
        
        try:
            cursor = self.collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).skip(offset).limit(limit)
            
            history = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["timestamp"] = doc["timestamp"].isoformat()
                doc["created_at"] = doc["created_at"].isoformat()
                history.append(doc)
            
            return history
        except Exception as e:
            print(f"Error retrieving chat history: {e}")
            return []
    
    def get_chat_context(self, user_id: str, limit: int = 10):
        """Get recent chat context for GPT memory"""
        if not self.collection:
            return []
        
        try:
            cursor = self.collection.find(
                {"user_id": user_id}
            ).sort("timestamp", -1).limit(limit)
            
            context = []
            for doc in cursor:
                context.append({
                    "question": doc["question"],
                    "answer": doc["answer"],
                    "timestamp": doc["timestamp"].isoformat()
                })
            
            return context
        except Exception as e:
            print(f"Error retrieving chat context: {e}")
            return []
    
    def delete_user_history(self, user_id: str):
        """Delete all chat history for a user"""
        if not self.collection:
            return False
        
        try:
            result = self.collection.delete_many({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting chat history: {e}")
            return False
    
    def get_chat_stats(self, user_id: str = None):
        """Get chat statistics"""
        if not self.collection:
            return {}
        
        try:
            pipeline = []
            if user_id:
                pipeline.append({"$match": {"user_id": user_id}})
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": None,
                        "total_chats": {"$sum": 1},
                        "unique_users": {"$addToSet": "$user_id"},
                        "avg_answer_length": {"$avg": {"$strLenCP": "$answer"}},
                        "files_used": {"$sum": {"$size": "$source_files"}}
                    }
                }
            ])
            
            result = list(self.collection.aggregate(pipeline))
            if result:
                stats = result[0]
                stats["unique_users"] = len(stats["unique_users"])
                return stats
            return {}
        except Exception as e:
            print(f"Error getting chat stats: {e}")
            return {}

# Initialize chat history manager
chat_history_manager = ChatHistoryManager()

# Fallback to file-based storage if MongoDB is not available
class FileBasedChatHistory:
    def __init__(self, file_path: str = "chat_history.json"):
        self.file_path = file_path
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def store_chat(self, user_id: str, question: str, answer: str, 
                   source_files: List[str] = None, metadata: Dict[str, Any] = None):
        try:
            with open(self.file_path, 'r') as f:
                history = json.load(f)
            
            chat_entry = {
                "id": str(len(history) + 1),
                "user_id": user_id,
                "question": question,
                "answer": answer,
                "source_files": source_files or [],
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            history.append(chat_entry)
            
            with open(self.file_path, 'w') as f:
                json.dump(history, f, indent=2)
            
            return chat_entry["id"]
        except Exception as e:
            print(f"Error storing chat to file: {e}")
            return None
    
    def get_user_history(self, user_id: str, limit: int = 50, offset: int = 0):
        try:
            with open(self.file_path, 'r') as f:
                history = json.load(f)
            
            user_history = [h for h in history if h["user_id"] == user_id]
            user_history.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return user_history[offset:offset + limit]
        except Exception as e:
            print(f"Error reading chat history: {e}")
            return []
    
    def get_chat_context(self, user_id: str, limit: int = 10):
        try:
            with open(self.file_path, 'r') as f:
                history = json.load(f)
            
            user_history = [h for h in history if h["user_id"] == user_id]
            user_history.sort(key=lambda x: x["timestamp"], reverse=True)
            
            context = []
            for doc in user_history[:limit]:
                context.append({
                    "question": doc["question"],
                    "answer": doc["answer"],
                    "timestamp": doc["timestamp"]
                })
            
            return context
        except Exception as e:
            print(f"Error reading chat context: {e}")
            return []

# Use file-based storage as fallback
if chat_history_collection is None:
    chat_history_manager = FileBasedChatHistory() 