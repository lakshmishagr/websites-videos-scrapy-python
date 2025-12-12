import scrapy
from slugify import slugify
from ..database.Queries import Queries
from subprocess import  check_output, CalledProcessError, STDOUT
from ..items import VideoItem

class BollywoodHungamaEng(scrapy.Spider):
    name="page_bollywoodhungamaeng"
    start_urls=[

        'https://www.bollywoodhungama.com/top-videos/',
        'https://www.bollywoodhungama.com/videos/making-of-the-music/',
        'https://www.bollywoodhungama.com/videos/movie-promos/',
        'https://www.bollywoodhungama.com/videos/celeb-interviews/',
        'https://www.bollywoodhungama.com/videos/making-of-movies/',
        'https://www.bollywoodhungama.com/videos/parties-events/',
        'https://www.bollywoodhungama.com/videos/first-day-first-show/',
        ]
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
    
    def parse(self, response):
        links = response.xpath(
            "//article[contains(@class, 'bh-cm-box')]/figure/a/@href | "
            "//div[contains(@class, 'video-list-box')]/figure/a/@href"
        ).getall()
        
        category = "entertainment"
        self.logger.info(f"Bollywood ENG Started. Found {len(links)} links on {response.url}")

        for link in links:
            yield scrapy.Request(
                url=link, 
                callback=self.parse_subpage,
                meta={'category': category}
            )

    def parse_subpage(self, response):
        try:
            video_url = response.xpath("//div/meta[@itemprop='contentURL']/@content").get()
            if not video_url:
                self.logger.warning(f"No video contentURL found on {response.url}")
                return

            title = response.xpath("//meta[@property = 'og:title']/@content").get()
            description = response.xpath("//meta[@property = 'og:description']/@content").get()
            image = response.xpath("//meta[@property = 'og:image']/@content").get()
            video_keywords_str = response.xpath("//meta[@name = 'keywords']/@content").get('')
            category = response.meta['category']

            # Get video duration using ffprobe
            duration_seconds = self._get_video_duration(video_url)
            if duration_seconds is None:
                self.logger.error(f"Could not get duration for video: {video_url}")
                return
            
            # Format duration to HH:MM:SS
            m, s = divmod(duration_seconds, 60)
            h, m = divmod(m, 60)
            modified_time = f"{int(h):02d}:{int(m):02d}:{int(s):02d}"

            modified_video_keywords = [kw.strip() for kw in video_keywords_str.split(',') if kw.strip()]
            keywords_db_ids = Queries.insert_keywords(self, modified_video_keywords)

            item = VideoItem()
            item['video_title'] = title
            item['video_slug'] = slugify(title)
            item['video_link'] = video_url
            item['video_description'] = description
            item['broadcaster'] = "5edf39ec820f925d307ae315"
            item['videoformat'] = "5ce4f7ffa5c038104cb76649"
            item['video_image'] = image
            item['videokeywords'] = keywords_db_ids
            item['page_url'] = response.url
            item['duration'] = modified_time
            item['category'] = category
            item['language'] = "english"
            item['keywords'] = ' | '.join(modified_video_keywords)

            if all([video_url, image, title]) and video_url.endswith(('.mp4', '.m3u8', '.m4v')):
                result = Queries.insert_api(self, dict(item))
                if result.status_code == 200:
                    self.logger.info(f"Successfully inserted video: {title}")
                else:
                    self.logger.error(f"API insert failed for {title} with status {result.status_code}: {result.text}")
            else:
                self.logger.warning(f"Skipping item due to missing data or invalid format: {title}")

        except Exception as err:
            self.logger.error(f"Error processing subpage {response.url}: {err}")

    def _get_video_duration(self, video_url):
        """Runs ffprobe to get video duration in seconds."""
        command = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', video_url
        ]
        try:
            # Added text=True for automatic decoding
            output = check_output(command, stderr=STDOUT, text=True)
            return float(output.strip())
        except (CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"ffprobe error for {video_url}: {e}")
            return None
        except ValueError:
            self.logger.error(f"ffprobe returned non-numeric duration for {video_url}")
            return None
