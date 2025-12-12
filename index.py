"""Main entry point for the video scraping project."""

import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from page_scraping.spiders.Ndtv import NdtvSpider

def main():
    """Run the scraping process."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get Scrapy settings
    settings = get_project_settings()
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    # Add spiders to crawl
    process.crawl(NdtvSpider)
    
    # Start crawling
    process.start()

if __name__ == '__main__':
    main()