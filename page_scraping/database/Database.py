"""Database connection for video scraping."""

from pymongo import MongoClient
from typing import Optional
import os


class Database:
    """MongoDB connection manager."""
    
    _client: Optional[MongoClient] = None
    _db = None
    
    @classmethod
    def get_client(cls) -> MongoClient:
        """Get MongoDB client with connection pooling."""
        if cls._client is None:
            # Environment-based configuration
            host = os.getenv('MONGO_HOST', 'localhost')
            port = int(os.getenv('MONGO_PORT', '27017'))
            username = os.getenv('MONGO_USERNAME')
            password = os.getenv('MONGO_PASSWORD')
            auth_source = os.getenv('MONGO_AUTH_SOURCE', 'admin')
            
            # Build connection string
            if username and password:
                uri = f"mongodb://{username}:{password}@{host}:{port}/{auth_source}"
            else:
                uri = f"mongodb://{host}:{port}"
            
            cls._client = MongoClient(
                uri,
                maxPoolSize=50,
                minPoolSize=5,
                maxIdleTimeMS=30000,
                serverSelectionTimeoutMS=5000
            )
        
        return cls._client
    
    @classmethod
    def get_database(cls):
        """Get database instance."""
        if cls._db is None:
            db_name = os.getenv('MONGO_DATABASE', 'video_scraper')
            cls._db = cls.get_client()[db_name]
        return cls._db
