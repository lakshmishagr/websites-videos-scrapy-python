"""Database queries for video scraping project."""

from __future__ import annotations
from typing import Any, Dict, List
import logging

from ..database.Database import Database
import pymongo
import requests
from slugify import slugify


class Queries:
    """Database operations for video scraping."""
    
    _db_collection = Database.db.broadcastersvideos
    _db_collection_keywords = Database.db.video_keywords
    logger = logging.getLogger(__name__)
    
    @classmethod
    def insert_videos(cls, video_data: Dict[str, Any]) -> bool:
        """Insert video data into database."""
        try:
            cls._db_collection.insert_one(video_data)
            cls.logger.info(f"Video inserted: {video_data.get('video_title', 'Unknown')}")
            return True
        except pymongo.errors.DuplicateKeyError:
            cls.logger.warning("Duplicate video encountered")
            return False
        except Exception as e:
            cls.logger.error(f"Failed to insert video: {e}")
            return False

    @classmethod
    def insert_keywords(cls, keywords: List[str]) -> List[str]:
        """Insert keywords and return their IDs."""
        keyword_ids = []
        
        for keyword in keywords:
            if not keyword.strip():
                continue
                
            keyword_slug = slugify(keyword)
            keyword_doc = {"name": keyword.strip(), "slug": keyword_slug}
            
            try:
                # Try to insert new keyword
                result = cls._db_collection_keywords.insert_one(keyword_doc)
                keyword_ids.append(str(result.inserted_id))
                cls.logger.debug(f"Keyword inserted: {keyword}")
            except pymongo.errors.DuplicateKeyError:
                # Keyword exists, get its ID
                try:
                    existing = cls._db_collection_keywords.find_one({"slug": keyword_slug})
                    if existing:
                        keyword_ids.append(str(existing['_id']))
                except Exception as e:
                    cls.logger.error(f"Failed to find existing keyword {keyword}: {e}")
            except Exception as e:
                cls.logger.error(f"Failed to process keyword {keyword}: {e}")
                
        return keyword_ids

    @classmethod
    def insert_api(cls, video_data: Dict[str, Any]) -> requests.Response:
        """Send video data to API endpoint."""
        api_url = 'https://your-strapi-backend.com/broadcastersvideos'
        
        try:
            response = requests.post(
                api_url, 
                json=video_data,  # Use json instead of data for better handling
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            cls.logger.error(f"API request failed: {e}")
            # Return a mock response object for error handling
            mock_response = requests.Response()
            mock_response.status_code = 500
            return mock_response