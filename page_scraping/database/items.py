"""Scrapy items for video data."""

import scrapy

class VideoItem(scrapy.Item):
    """Simplified video item with essential fields only."""
    title = scrapy.Field()
    video_url = scrapy.Field()
    page_url = scrapy.Field()
    description = scrapy.Field()
    thumbnail = scrapy.Field()
    duration = scrapy.Field()
    source = scrapy.Field()
    category = scrapy.Field()
    language = scrapy.Field()
    slug = scrapy.Field()