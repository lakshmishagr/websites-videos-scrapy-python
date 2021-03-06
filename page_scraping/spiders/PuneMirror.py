from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys
from slugify import slugify
from ..database.Queries import Queries

url=""
modified_time=""

class PuneMirror(scrapy.Spider):
    name='page_pune'
    start_urls = [
        'https://punemirror.indiatimes.com/videos/news',
        'https://punemirror.indiatimes.com/videos/videolist/msid-4928483,more-1.cms',
        'https://punemirror.indiatimes.com/videos/videolist/msid-36747721,more-1.cms',
        'https://punemirror.indiatimes.com/videos/videolist/msid-3813456,more-1.cms',
        'https://punemirror.indiatimes.com/videos/lifestyle',
        'https://punemirror.indiatimes.com/videos/business',
        'https://punemirror.indiatimes.com/videos/funny',
        'https://punemirror.indiatimes.com/videos/celebs'
    ]

    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        lang = "english"
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        print(category)
        if ("news" in category):
            category = "news"
        if ("msid-4928483,more-1.cms" in category):
            category = "entertainment"
        if ("msid-36747721,more-1.cms" in category):
            category = "entertainment|movies"
        if ("lifestyle" in category):
            category = "lifestyle"
        if ("msid-3813456,more-1.cms" in category):
            category = "sports"
        if ("business" in category):
            category = "business"
        if ("funny" in category):
            category = "funny"
        if ("celebs" in category):
            category = "celebrity"

        links = hxs.xpath("//span[@class='videoThumb']/a/@href").extract()
        print("PUNEMIRROR Started")
        # links= links[0:1]
        for link in links:
            url = domain+link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            yield request
       
    
    def parse_subpage(self, response):
        try:
            global video_url, url, duration, video_keywords, title, description, image, modified_video_keywords, modified_time, category, lang
            try:
                video_url = response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl":"(.+)"')[0]
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords = response.xpath("//meta[@property = 'video:tag']/@content").extract_first()
                category = response.meta['category']
                lang = response.meta['lang']
            except:
                print("EXCEPTION HIT")

            try:
                duration=response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration":"(.+)"')[0]
                duration = duration.replace('T','0:').replace('M', ':').replace('S','')
                print("\n duration", duration)
                time = duration.split(':')
                if (len(time[0]) < 2):
                    time[0] = '0' + time[0]
                if (len(time[1]) < 2):
                    time[1] = '0' + time[1]
                if (len(time[2]) < 2):
                    time[2] = '0' + time[2]
                modified_time = str(time[0] + ":" + time[1] + ":" + time[2])

            except:
                print("ERROR")
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split(",")]
            except:
                print("SPLIT ERROR")
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d00d4068fab72490ef1c97d",
                "videoformat" : "5ce4f7ffa5c038104cb76649",
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
                # print("aaa------------------aaaa")
                # print(title)
                # print(video_url)
                # print(modified_time)
                # print(image)
                # print(category)
                # print(lang)
                # # print(insertObject)
                # print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result.json())

        except:
            print("URL MISSING")
