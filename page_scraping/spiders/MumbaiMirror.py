from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries

class MumbaiMirror(scrapy.Spider):
    name="page_mumbaimirror"
    start_urls=[

        'https://mumbaimirror.indiatimes.com/videos/top-videos',
        'https://mumbaimirror.indiatimes.com/videos/bollywood',
        'https://mumbaimirror.indiatimes.com/videos/viral-videos',
        'https://mumbaimirror.indiatimes.com/videos/entertainment/videolist/12893173.cms',
        'https://mumbaimirror.indiatimes.com/videos/sports',
        'https://mumbaimirror.indiatimes.com/videos/mumbai',
        'https://mumbaimirror.indiatimes.com/videos/mirror-originals',
        'https://mumbaimirror.indiatimes.com/videos/politics',
        'https://mumbaimirror.indiatimes.com/videos/horoscope',
        'https://mumbaimirror.indiatimes.com/videos/',
        ]
    def parse(self, response):
        hxs = Selector(response)
        links1 = hxs.xpath("//span[@class = 'vidThumbMain']/a/@href").extract()
        links2 = hxs.xpath("//span[@class = 'videoThumb']/a/@href").extract()
        # links = hxs.xpath("//a[@class = 'w_img']/@href").extract()
        links = links2 + links1
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        if ("top-videos" in category):
            category = "news"
        if ("bollywood" in category):
            category = "entertainment"
        if ("viral-videos" in category):
            category = "news"
        if ("entertainment" in category):
            category = "entertainment"
        if ("mumbai" in category):
            category = "city|mumbai"
        if ("mirror-originals" in category):
            category = "entertainment"
        if ("sports" in category):
            category = "sports"
        if ("politics" in category):
            category = "politics"
        if ("horoscope" in category):
            category = "horoscope"
        if ("videos" in category and len(category) == 2):
            category = "news"

        print("MUMBAIMIRROR Started")
        print(len(links))
        # links = links[0:1]
        for link in links:
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain + link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request


    def parse_subpage(self, response):
        print("subvalues")
        try:
            global video_url, duration, video_keywords, title, description, image, modified_video_keywords, modified_time, category
            try:
                video_url=response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl":"(.+)"')[0]
                duration=response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration":"(.+)"')[0]
                video_keywords=response.xpath('//script[@type = "application/ld+json"]/text()').re('"keywords":"(.+)"')[0]
                duration = duration.replace('T','0:').replace('M', ':').replace('S','')
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                category = response.meta['category']

            except:
                print("EXCEPTION HIT")
            try:
                time = duration.split(':')
                if (len(time[0]) < 2):
                    time[0] = '0' + time[0]
                if (len(time[1]) < 2):
                    time[1] = '0' + time[1]
                if (len(time[2]) < 2):
                    time[2] = '0' + time[2]
                modified_time = str(time[0] + ":" + time[1] + ":" + time[2])
            except:
                print("TIME ERROR")
            modified_video_keywords = [x.strip() for x in video_keywords.split()]

            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d3e99033b6d5e43e2ef58e5",   #Not yet changed
                "videoformat" : "5ce4f7eda5c038104cb76648",   #Not yet changed
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration" : modified_time,
                "category": category,
                "language": "english",
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
                # print("english")
                # # print(insertObject)
                # print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result.json())

        except Exception as err:
            print("mumbaimirror error", err)
