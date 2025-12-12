"""Scrapy items for video data."""

import scrapy


class VideoItem(scrapy.Item):
    """Video item definition."""
    title = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    thumbnail = scrapy.Field()
    duration = scrapy.Field()
    published_date = scrapy.Field()
    source = scrapy.Field()
    category = scrapy.Field()
    tags = scrapy.Field()
    slug = scrapy.Field()