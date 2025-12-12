"""Scrapy settings for page_scraping project."""

BOT_NAME = 'page_scraping'

SPIDER_MODULES = ['page_scraping.spiders']
NEWSPIDER_MODULE = 'page_scraping.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure pipelines
ITEM_PIPELINES = {
    'page_scraping.pipelines.DuplicatesPipeline': 300,
    'page_scraping.pipelines.VideoPipeline': 400,
}

# Configure delays and concurrency
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 8

# User agent
USER_AGENT = 'page_scraping (+http://www.yourdomain.com)'

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

# Logging
LOG_LEVEL = 'INFO'

# Request fingerprinting
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'