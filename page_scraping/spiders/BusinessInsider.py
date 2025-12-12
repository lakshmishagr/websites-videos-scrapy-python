from urllib.parse import urlparse, urlunparse
import scrapy
import json
from slugify import slugify
from subprocess import run, CalledProcessError, PIPE
from ..database.Queries import Queries
from ..items import VideoItem
import re

class BusinessInsider(scrapy.Spider):
    name="page_businessinsider"
    start_urls=[
        'https://www.businessinsider.in/videos/finance',
        'https://www.businessinsider.in/videos/advertising/',
        'https://www.businessinsider.in/videos/tech',
        'https://www.businessinsider.in/videos/business',
        'https://www.businessinsider.in/videos/life',
        'https://www.businessinsider.in/videos/entertainment',
        'https://www.businessinsider.in/videos/strategy',
        ]
    
    # A mapping from URL path segments to categories
    CATEGORY_MAP = {
        "finance": "economics",
        "business": "business",
        "tech": "technology",
        "advertising": "opinions",
        "life": "lifestyle",
        "strategy": "opinions",
        "entertainment": "entertainment",
    }

    def parse(self, response):
        parsed_uri = urlparse(response.url)
        lang = "english"
        path_segment = parsed_uri.path.strip('/').split('/')[-1]
        category = self.CATEGORY_MAP.get(path_segment, "news")

        links = response.xpath("//a[@class = 'video-img-link']/@href").getall()
        self.logger.info(f"Businessinsider Started. Found {len(links)} links on {response.url}")

        for link in links:
            yield scrapy.Request(
                url=link, 
                callback=self.parse_subpage,
                meta={'category': category, 'lang': lang}
            )

    def parse_subpage(self, response):
        try:
            json_ld_str = response.xpath('//script[@type = "application/ld+json"]/text()').get()
            if not json_ld_str:
                self.logger.warning(f"No LD+JSON data found on {response.url}")
                return
            
            json_data = json.loads(json_ld_str)
            video_url = json_data.get('contentUrl')
            if not video_url:
                self.logger.warning(f"No contentUrl found in LD+JSON on {response.url}")
                return

            title = response.xpath("//meta[@property = 'og:title']/@content").get()
            description = response.xpath("//meta[@property = 'og:description']/@content").get()
            image = response.xpath("//meta[@property = 'og:image']/@content").get()
            video_keywords_str = response.xpath("//meta[@name = 'keywords']/@content").get('')
            category = response.meta['category']
            lang = response.meta['lang']

            # Get video duration using ffprobe
            duration_seconds = self._get_video_duration(video_url)
            if duration_seconds is None:
                self.logger.warning(f"Could not get duration for video: {video_url}, using default")
                modified_time = "00:00:00"
            else:
                # Format duration to HH:MM:SS using modern approach
                h, remainder = divmod(int(duration_seconds), 3600)
                m, s = divmod(remainder, 60)
                modified_time = f"{h:02d}:{m:02d}:{s:02d}"

            modified_video_keywords = [kw.strip() for kw in video_keywords_str.split(',') if kw.strip()]
            keywords_db_ids = Queries.insert_keywords(self, modified_video_keywords)

            item = VideoItem()
            item['video_title'] = title
            item['video_slug'] = slugify(title)
            item['video_link'] = video_url
            item['video_description'] = description
            item['broadcaster'] = "5ee2370ebddf2287a9cb20b5"
            item['videoformat'] = "5ce4f7eda5c038104cb76648"
            item['video_image'] = image
            item['videokeywords'] = keywords_db_ids
            item['page_url'] = response.url
            item['duration'] = modified_time
            item['category'] = category
            item['language'] = lang
            item['keywords'] = ' | '.join(modified_video_keywords)

            # Simplified validation and insertion
            if self._is_valid_item(video_url, image, title):
                try:
                    result = Queries.insert_api(self, dict(item))
                    if result.status_code == 200:
                        self.logger.info(f"Successfully inserted video: {title}")
                    else:
                        self.logger.error(f"API insert failed for {title} with status {result.status_code}")
                except Exception as e:
                    self.logger.error(f"Failed to insert video {title}: {e}")
            else:
                self.logger.warning(f"Skipping invalid item: {title}")

        except Exception as err:
            self.logger.error(f"Error processing subpage {response.url}: {err}")
    
    def _is_valid_item(self, video_url: str, image: str, title: str) -> bool:
        """Validate required fields and video format."""
        return (
            all([video_url, image, title]) and 
            video_url.endswith(('.mp4', '.m3u8', '.webm', '.mov'))
        )

    def _get_video_duration(self, video_url: str) -> float | None:
        """Safely runs ffprobe to get video duration in seconds."""
        # Security: Validate URL format and protocol
        if not self._is_valid_video_url(video_url):
            self.logger.error(f"Invalid or unsafe video URL: {video_url}")
            return None
            
        command = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', video_url
        ]
        try:
            result = run(command, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                self.logger.error(f"ffprobe failed for {video_url}: {result.stderr}")
                return None
        except (CalledProcessError, FileNotFoundError, TimeoutError) as e:
            self.logger.error(f"ffprobe error for {video_url}: {e}")
            return None
        except ValueError:
            self.logger.error(f"ffprobe returned non-numeric duration for {video_url}")
            return None
    
    def _is_valid_video_url(self, url: str) -> bool:
        """Validate video URL for security."""
        try:
            parsed = urlparse(url)
            # Only allow http/https protocols
            if parsed.scheme not in ('http', 'https'):
                return False
            # Basic URL format validation
            if not parsed.netloc:
                return False
            # Check for suspicious characters that could be used for injection
            if re.search(r'[;&|`$(){}\[\]<>]', url):
                return False
            return True
        except Exception:
            return False
