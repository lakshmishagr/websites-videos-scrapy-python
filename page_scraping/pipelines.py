"""Scrapy pipelines for processing scraped data."""

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from .database.Queries import VideoRepository
import logging


class VideoPipeline:
    """Pipeline to save videos to database."""
    
    def __init__(self):
        self.video_repo = VideoRepository()
        self.logger = logging.getLogger(__name__)
    
    def process_item(self, item, spider):
        """Process and save video item."""
        adapter = ItemAdapter(item)
        
        # Convert to dict
        video_data = dict(adapter)
        
        # Save to database
        if self.video_repo.save_video(video_data):
            self.logger.info(f"Saved video: {video_data.get('title', 'Unknown')}")
        else:
            self.logger.error(f"Failed to save video: {video_data.get('title', 'Unknown')}")
        
        return item


class DuplicatesPipeline:
    """Pipeline to filter duplicate videos."""
    
    def __init__(self):
        self.video_repo = VideoRepository()
    
    def process_item(self, item, spider):
        """Check for duplicates."""
        adapter = ItemAdapter(item)
        slug = adapter.get('slug')
        
        if slug and self.video_repo.video_exists(slug):
            raise DropItem(f"Duplicate video found: {slug}")
        
        return item