"""Database connection for video scraping."""

from pymongo import MongoClient
from typing import Optional
import os


class Database:
    """MongoDB database connection."""
    
    _client: Optional[MongoClient] = None
    _db = None
    
    @classmethod
    def get_client(cls) -> MongoClient:
        """Get MongoDB client instance."""
        if cls._client is None:
            # Use environment variables for configuration
            host = os.getenv('MONGO_HOST', 'localhost')
            port = int(os.getenv('MONGO_PORT', '27017'))
            username = os.getenv('MONGO_USERNAME')
            password = os.getenv('MONGO_PASSWORD')
            auth_source = os.getenv('MONGO_AUTH_SOURCE', 'admin')
            
            if username and password:
                cls._client = MongoClient(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    authSource=auth_source
                )
            else:
                cls._client = MongoClient(host, port)
        
        return cls._client
    
    @classmethod
    def get_database(cls):
        """Get database instance."""
        if cls._db is None:
            db_name = os.getenv('MONGO_DATABASE', 'video_scraper')
            cls._db = cls.get_client()[db_name]
        return cls._db
