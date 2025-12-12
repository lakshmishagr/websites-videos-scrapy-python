"""Database operations for video scraping."""

from typing import Dict, Any
import logging
from datetime import datetime

from .Database import Database
from slugify import slugify


class VideoRepository:
    """Video database operations."""
    
    def __init__(self):
        self.db = Database.get_database()
        self.collection = self.db.videos
        self.logger = logging.getLogger(__name__)
        
        # Create indexes for performance
        self.collection.create_index([('slug', 1)], unique=True, background=True)
        self.collection.create_index([('source', 1), ('created_at', -1)], background=True)
    
    def save_video(self, video_data: Dict[str, Any]) -> bool:
        """Save video to database."""
        try:
            # Add timestamps
            video_data['created_at'] = datetime.utcnow()
            video_data['updated_at'] = datetime.utcnow()
            
            # Generate slug if missing
            if 'slug' not in video_data and 'title' in video_data:
                video_data['slug'] = slugify(video_data['title'])
            
            # Upsert video
            result = self.collection.update_one(
                {'slug': video_data['slug']},
                {'$set': video_data},
                upsert=True
            )
            
            action = "created" if result.upserted_id else "updated"
            self.logger.info(f"Video {action}: {video_data.get('title', 'Unknown')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save video: {e}")
            return False
    
    def video_exists(self, slug: str) -> bool:
        """Check if video exists by slug."""
        return self.collection.find_one({'slug': slug}) is not None