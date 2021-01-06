from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from subprocess import  check_output, CalledProcessError, STDOUT
from ..database.Queries import Queries

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
    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        lang = "english"
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        if ("finance" in category):
            category = "economics"
        if ("business" in category):
            category = "business"
        if ("tech" in category):
            category = "technology"
        if ("advertising" in category):
            category = "opinions"
        if ("life" in category):
            category = "lifestyle"
        if ("strategy" in category):
            category = "opinions"
        if ("entertainment" in category):
            category = "entertainment"
        if ("video" in category and (len(category) == 2 or len(category) == 3)):
            category = "news"

        links = hxs.xpath("//a[@class = 'video-img-link']/@href").extract()
        print("Businessinsider Started")
        for link in links:
            url = link
            # yield scrapy.Request(url, callback=self.parse_subpage)
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            yield request
    def parse_subpage(self, response):
        print("subvalues")
        try:
            global video, url, duration, title, description, image, video_keywords, modified_time, modified_video_keywords,category,lang, video_url
            try:
                video_url = response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl": "(.+)"')[0]
                url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
                duration = None
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
                category = response.meta['category']
                lang = response.meta['lang']

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

                if (duration == None):
                    output = check_output(command, stderr=STDOUT).decode()
                    duration = round(float(output) / 60, 2)
                    duration = str(duration).replace('.', ':')
                    duration = '0:' + duration
                else:
                    duration = round(float(duration) / 60, 2)
                    duration = str(duration).replace('.', ':')
                    duration = '0:' + duration

            except Exception as err:
                print("EXCEPTION HIT",err)
            try:
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
                time2 = time[1] if int(time[1]) > 9 else '0'+time[1]
                time3 = time[2] #if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1+":"+time2+":"+time3)

            except Exception as err:
                print("TIME ERROR",err)

            modified_video_keywords = [x.strip() for x in video_keywords.split()]

            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5ee2370ebddf2287a9cb20b5",   #Not yet changed
                "videoformat" : "5ce4f7eda5c038104cb76648",   #Not yet changed
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration" : modified_time,
                "category": category,
                "language": lang,
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }
            if ((len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8) and
                    (video_url.endswith('.mp4') or video_url.endswith('.m3u8'))):
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result)
        except Exception as err:
            print("URL MISSING",err)
