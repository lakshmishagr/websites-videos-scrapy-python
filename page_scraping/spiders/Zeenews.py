"""Zeenews video spider."""

from typing import Generator, Optional
from urllib.parse import urljoin, urlparse
import scrapy
import re

from ..items import VideoItem


class ZeenewsSpider(scrapy.Spider):
    """Spider for scraping videos from Zeenews."""
    
    name = 'zeenews'
    allowed_domains = ['zeenews.india.com']
    start_urls = ['https://zeenews.india.com/video']
    
    def parse(self, response) -> Generator[scrapy.Request, None, None]:
        """Parse main video page and extract video links."""
        self.logger.info("Starting Zeenews video scraping")
        
        # Extract video links
        video_links = response.xpath(
            "//div[@class='mini-video mini-video-h margin-bt30px']/a/@href | "
            "//div[@class='mini-video margin-bt10px']/a/@href"
        ).getall()
        
        for link in video_links:
            video_url = urljoin(response.url, link)
            yield scrapy.Request(
                url=video_url,
                callback=self.parse_video,
                meta={'category': 'news'}
            )
    
    def parse_video(self, response) -> Optional[VideoItem]:
        """Parse individual video page."""
        try:
            # Extract video data
            video_code = response.xpath(
                "//div[@class='video-page-block pos-relative margin-bt40px']"
                "//div[@class='video-img']/div/@video-code"
            ).get()
            
            title = response.xpath("//meta[@property='og:title']/@content").get()
            description = response.xpath("//meta[@property='og:description']/@content").get()
            image_url = response.xpath("//meta[@property='og:image']/@content").get()
            
            # Extract keywords
            keywords_list = response.xpath("//meta[@property='article:tag']/@content").getall()
            keywords = ', '.join(keywords_list) if keywords_list else ''
            
            # Extract and format duration
            duration = self._extract_duration(response)
            
            # Validate required fields
            if not all([video_code, title, image_url, duration]):
                self.logger.warning(f"Missing required fields for {response.url}")
                return None
            
            # Create video item
            item = VideoItem()
            item['title'] = title.strip()
            item['url'] = video_code
            item['description'] = description.strip() if description else ''
            item['image_url'] = image_url
            item['duration'] = duration
            item['category'] = response.meta.get('category', 'news')
            item['language'] = 'hindi'
            item['keywords'] = keywords
            item['source_url'] = response.url
            item['broadcaster'] = self.name
            
            return item
            
        except Exception as e:
            self.logger.error(f"Error parsing video {response.url}: {e}")
            return None
    
    def _extract_duration(self, response) -> str:
        """Extract and format video duration."""
        try:
            # Extract duration from JSON-LD
            duration_match = response.xpath(
                "//script[@type='application/ld+json']/text()"
            ).re_first(r'"duration":\s*"([^"]+)"')
            
            if not duration_match:
                return '00:00:00'
            
            # Convert PT format to HH:MM:SS
            duration = duration_match.replace('PT', '').replace('M', ':').replace('S', '')
            
            # Ensure proper format
            parts = duration.split(':')
            if len(parts) == 2:
                minutes, seconds = parts
                return f"00:{int(minutes):02d}:{int(seconds):02d}"
            elif len(parts) == 3:
                hours, minutes, seconds = parts
                return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            
        except Exception as e:
            self.logger.warning(f"Error extracting duration: {e}")
        
        return '00:00:00'
