# Video Scraping Project

A Scrapy-based web scraping project for collecting video content from various news websites.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure MongoDB connection in `page_scraping/database/Database.py`

3. Run the scraper:
```bash
python index.py
```

## Project Structure

- `page_scraping/spiders/` - Spider implementations for different websites
- `page_scraping/database/` - Database connection and operations
- `page_scraping/items.py` - Data structure definitions
- `page_scraping/pipelines.py` - Data processing pipelines
- `page_scraping/settings.py` - Scrapy configuration

## Features

- MongoDB integration for data storage
- Duplicate detection and filtering
- Configurable crawling delays and concurrency
- Comprehensive logging
- Modular spider architecture