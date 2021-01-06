from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html
from slugify import slugify
from ..database.Queries import Queries
from subprocess import check_output, CalledProcessError, STDOUT
import subprocess
from time import strftime
from time import gmtime
# from moviepy.video.io.VideoFileClip import VideoFileClip

class TeluguNews18(scrapy.Spider):
    name="page_telugunews18"
    start_urls=[
        'https://telugu.news18.com/videos/uncategorized/',
        'https://telugu.news18.com/videos/international/',
        'https://telugu.news18.com/videos/trending/',
        'https://telugu.news18.com/videos/andhra-pradesh/',
        'https://telugu.news18.com/videos/sports/',
        'https://telugu.news18.com/videos/national/',
        'https://telugu.news18.com/videos/telangana/',
        'https://telugu.news18.com/videos/business/',
        'https://telugu.news18.com/videos/movies/'
        ]
    # user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
    def parse(self, response):
        hxs = Selector(response)
        links = hxs.xpath("//div[@class = 'featured_carousel']/ul/li/figure/a/@href").extract()
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        print("\n cat", category)
        if ("sports" in category):
            category = "sports"
        if ("international" in category):
            category = "news"
        if ("uncategorized" in category):
            category = "news"
        if ("movies" in category):
            category = "entertainment"
        if ("andhra-prades" in category):
            category = "news"
        if ("trending" in category):
            category = "news"
        if ("national" in category):
            category = "news"
        if ("telangana" in category):
            category = "news"
        if ("business" in category):
            category = "financial"

        print("TELEGUNEWS18 Started")
        for link in links:
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain+link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            print("\nfinal", category)
            yield request
    def parse_subpage(self, response):
        global video_url, url, duration, video_keywords, title, description, image, modified_video_keywords, modified_time
        try:
            video_url=response.xpath('//script[contains(., "var IS_THIRDPARTYJSAllow")]/text()').re('var hls_stream_url += "(.+)"')[0]

            command = [
                    'ffprobe',
                    '-v',
                    'error',
                    '-show_entries',
                    'format=duration',
                    '-of',
                    'default=noprint_wrappers=1:nokey=1',
                    video_url
                ]
            try:
                output = check_output( command, stderr=STDOUT ).decode()
                duration = round(float(output)/60, 2)
                duration = str(duration).replace('.', ':')
                duration = '0:'+duration
                print(duration)
            except CalledProcessError as e:
                output = e.output.decode()

            title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
            description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
            image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
            video_keywords = response.xpath("//meta[@name = 'news_keywords']/@content").extract_first()
            modified_video_keywords = [x.strip() for x in video_keywords.split()]
            category = response.meta['category']
            keywords = Queries.insert_keywords(self, modified_video_keywords)

            insertObject = {

                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d5b8e6411857574e9d440d9",   #Not yet changed
                "videoformat" : "5ce4f7ffa5c038104cb76649",   #Not yet changed
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url" : response.url,
                "duration" : duration,
                "category": category,
                "language": "telugu",
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }
            if ((len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8) and
                    (video_url.endswith('.mp4') or video_url.endswith('.m3u8') or video_url.endswith('.m4v'))):
                # print("aaa------------------aaaa")
                # print(title)
                # print(video_url)
                # print(modified_time)
                # print(image)
                # print(category)
                # print("english")
                # print(insertObject)
                # print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result.json())

        except Exception as err:
            print("BollywoodEng error", err)
