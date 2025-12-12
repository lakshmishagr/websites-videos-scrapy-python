"""Scrapy items for video scraping project."""

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst
from w3lib.html import remove_tags


def remove_whitespace(value: str) -> str:
    """Remove leading/trailing whitespace."""
    return value.strip()


class VideoItem(scrapy.Item):
    """Item for scraped video data."""
    video_title = scrapy.Field()
    video_slug = scrapy.Field()
    video_link = scrapy.Field()
    video_description = scrapy.Field()
    broadcaster = scrapy.Field()
    videoformat = scrapy.Field()
    video_image = scrapy.Field()
    videokeywords = scrapy.Field()
    page_url = scrapy.Field()
    duration = scrapy.Field()
    category = scrapy.Field()
    language = scrapy.Field()
    keywords = scrapy.Field()


class AbpLiveItem(scrapy.Item):
    """Legacy item - consider removing if unused."""
    joke_text = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_whitespace),
        output_processor=TakeFirst()
    )
