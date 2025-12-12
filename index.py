"""Main entry point for video scraping."""

import logging
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from page_scraping.spiders.NdtvSpider import NdtvSpider


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Run video scraping process."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Load Scrapy settings
        settings = get_project_settings()
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Add spiders
        process.crawl(NdtvSpider)
        
        # Start scraping
        logger.info("Starting video scraping...")
        process.start()
        
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()