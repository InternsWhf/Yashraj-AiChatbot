from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import os
from pymongo import MongoClient
from collections import defaultdict, Counter

# MongoDB connection for analytics - Made optional
analytics_collection = None
events_collection = None
client = None

# Only try to connect if MongoDB is explicitly configured
mongodb_uri = os.getenv("MONGODB_URI")
if mongodb_uri:
try:
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
        # Test connection
        client.admin.command('ping')
    db = client["whf_chatbot"]
    analytics_collection = db["analytics"]
    events_collection = db["events"]
    print("✅ Connected to MongoDB for analytics")
except Exception as e:
    print(f"❌ MongoDB analytics connection failed: {e}")
    analytics_collection = None
    events_collection = None
    client = None
else:
    print("ℹ️ MongoDB not configured - using file-based analytics")

class AnalyticsManager:
    def __init__(self):
        self.analytics_collection = analytics_collection
        self.events_collection = events_collection
    
    def log_event(self, event_type: str, user_id: str = None, data: Dict[str, Any] = None):
        """Log an analytics event"""
        if self.events_collection is None:
            return None
        
        event = {
            "event_type": event_type,
            "user_id": user_id,
            "data": data or {},
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        try:
            result = self.events_collection.insert_one(event)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error logging event: {e}")
            return None
    
    def log_file_upload(self, user_id: str, file_name: str, file_type: str, file_size: int):
        """Log file upload event"""
        return self.log_event("file_upload", user_id, {
            "file_name": file_name,
            "file_type": file_type,
            "file_size": file_size
        })
    
    def log_query(self, user_id: str, question: str, has_context: bool, response_time: float):
        """Log query event"""
        return self.log_event("query", user_id, {
            "question": question,
            "has_context": has_context,
            "response_time": response_time
        })
    
    def log_login(self, user_id: str, login_method: str):
        """Log user login event"""
        return self.log_event("login", user_id, {
            "login_method": login_method
        })
    
    def get_dashboard_stats(self, days: int = 30):
        """Get comprehensive dashboard statistics"""
        if self.events_collection is None:
            return self._get_mock_stats()
        
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Pipeline for comprehensive stats
            pipeline = [
                {"$match": {"timestamp": {"$gte": start_date}}},
                {
                    "$group": {
                        "_id": {
                            "event_type": "$event_type",
                            "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}
                        },
                        "count": {"$sum": 1},
                        "users": {"$addToSet": "$user_id"}
                    }
                },
                {"$sort": {"_id.date": 1}}
            ]
            
            results = list(self.events_collection.aggregate(pipeline))
            
            # Process results
            stats = {
                "total_events": 0,
                "unique_users": set(),
                "file_uploads": 0,
                "queries": 0,
                "logins": 0,
                "daily_stats": defaultdict(lambda: {
                    "file_uploads": 0,
                    "queries": 0,
                    "logins": 0,
                    "users": set()
                }),
                "file_types": Counter(),
                "query_success_rate": 0,
                "avg_response_time": 0
            }
            
            for result in results:
                event_type = result["_id"]["event_type"]
                date = result["_id"]["date"]
                count = result["count"]
                users = result["users"]
                
                stats["total_events"] += count
                stats["unique_users"].update(users)
                stats["daily_stats"][date]["users"].update(users)
                
                if event_type == "file_upload":
                    stats["file_uploads"] += count
                    stats["daily_stats"][date]["file_uploads"] += count
                elif event_type == "query":
                    stats["queries"] += count
                    stats["daily_stats"][date]["queries"] += count
                elif event_type == "login":
                    stats["logins"] += count
                    stats["daily_stats"][date]["logins"] += count
            
            # Convert sets to counts
            stats["unique_users"] = len(stats["unique_users"])
            for date in stats["daily_stats"]:
                stats["daily_stats"][date]["users"] = len(stats["daily_stats"][date]["users"])
            
            # Get file type distribution
            file_events = self.events_collection.find({
                "event_type": "file_upload",
                "timestamp": {"$gte": start_date}
            })
            
            for event in file_events:
                file_type = event.get("data", {}).get("file_type", "unknown")
                stats["file_types"][file_type] += 1
            
            # Calculate query success rate
            query_events = list(self.events_collection.find({
                "event_type": "query",
                "timestamp": {"$gte": start_date}
            }))
            
            if query_events:
                successful_queries = sum(1 for event in query_events if event.get("data", {}).get("has_context", False))
                stats["query_success_rate"] = (successful_queries / len(query_events)) * 100
                
                response_times = [event.get("data", {}).get("response_time", 0) for event in query_events]
                stats["avg_response_time"] = sum(response_times) / len(response_times)
            
            return stats
            
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return self._get_mock_stats()
    
    def get_user_activity(self, user_id: str, days: int = 30):
        """Get activity statistics for a specific user"""
        if self.events_collection is None:
            return {}
        
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            pipeline = [
                {
                    "$match": {
                        "user_id": user_id,
                        "timestamp": {"$gte": start_date}
                    }
                },
                {
                    "$group": {
                        "_id": "$event_type",
                        "count": {"$sum": 1},
                        "last_activity": {"$max": "$timestamp"}
                    }
                }
            ]
            
            results = list(self.events_collection.aggregate(pipeline))
            
            activity = {
                "total_events": 0,
                "file_uploads": 0,
                "queries": 0,
                "logins": 0,
                "last_activity": None
            }
            
            for result in results:
                event_type = result["_id"]
                count = result["count"]
                last_activity = result["last_activity"]
                
                activity["total_events"] += count
                activity[event_type] = count
                
                if not activity["last_activity"] or last_activity > activity["last_activity"]:
                    activity["last_activity"] = last_activity
            
            return activity
            
        except Exception as e:
            print(f"Error getting user activity: {e}")
            return {}
    
    def _get_mock_stats(self):
        """Return mock statistics when MongoDB is not available"""
        return {
            "total_events": 150,
            "unique_users": 25,
            "file_uploads": 45,
            "queries": 89,
            "logins": 16,
            "daily_stats": {
                "2025-07-29": {"file_uploads": 5, "queries": 12, "logins": 2, "users": 8},
                "2025-07-28": {"file_uploads": 8, "queries": 15, "logins": 3, "users": 10},
                "2025-07-27": {"file_uploads": 12, "queries": 22, "logins": 4, "users": 12}
            },
            "file_types": {"pdf": 25, "xlsx": 12, "docx": 8},
            "query_success_rate": 78.5,
            "avg_response_time": 2.3
        }

# Initialize analytics manager
analytics_manager = AnalyticsManager()

# File-based analytics fallback
class FileBasedAnalytics:
    def __init__(self, file_path: str = "analytics.json"):
        self.file_path = file_path
        self.ensure_file_exists()
    
    def ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def log_event(self, event_type: str, user_id: str = None, data: Dict[str, Any] = None):
        try:
            with open(self.file_path, 'r') as f:
                events = json.load(f)
            
            event = {
                "id": str(len(events) + 1),
                "event_type": event_type,
                "user_id": user_id,
                "data": data or {},
                "timestamp": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            events.append(event)
            
            with open(self.file_path, 'w') as f:
                json.dump(events, f, indent=2)
            
            return event["id"]
        except Exception as e:
            print(f"Error logging event to file: {e}")
            return None
    
    def log_file_upload(self, user_id: str, file_name: str, file_type: str, file_size: int):
        return self.log_event("file_upload", user_id, {
            "file_name": file_name,
            "file_type": file_type,
            "file_size": file_size
        })
    
    def log_query(self, user_id: str, question: str, has_context: bool, response_time: float):
        return self.log_event("query", user_id, {
            "question": question,
            "has_context": has_context,
            "response_time": response_time
        })
    
    def log_login(self, user_id: str, login_method: str):
        return self.log_event("login", user_id, {
            "login_method": login_method
        })

# Use file-based analytics as fallback
if analytics_collection is None:
    analytics_manager = FileBasedAnalytics() 