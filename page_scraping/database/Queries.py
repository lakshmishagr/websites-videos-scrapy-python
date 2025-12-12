"""Database operations for video scraping."""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

from .Database import Database
import pymongo
from slugify import slugify


class VideoRepository:
    """Simplified video database operations."""
    
    def __init__(self):
        self.db = Database.get_database()
        self.collection = self.db.videos
        self.logger = logging.getLogger(__name__)
        
        # Create index for better performance
        self.collection.create_index([('slug', 1)], unique=True, background=True)
    
    def save_video(self, video_data: Dict[str, Any]) -> bool:
        """Save video to database."""
        try:
            # Add metadata
            video_data['created_at'] = datetime.utcnow()
            video_data['updated_at'] = datetime.utcnow()
            
            # Generate slug if not provided
            if 'slug' not in video_data and 'title' in video_data:
                video_data['slug'] = slugify(video_data['title'])
            
            # Use upsert to handle duplicates
            result = self.collection.update_one(
                {'slug': video_data['slug']},
                {'$set': video_data},
                upsert=True
            )
            
            if result.upserted_id:
                self.logger.info(f"New video saved: {video_data.get('title', 'Unknown')}")
            else:
                self.logger.info(f"Video updated: {video_data.get('title', 'Unknown')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save video: {e}")
            return False
    
    def video_exists(self, slug: str) -> bool:
        """Check if video already exists."""
        return self.collection.find_one({'slug': slug}) is not None