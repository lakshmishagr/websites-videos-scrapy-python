from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json, sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries
import urllib


class Bgr(scrapy.Spider):
    name = "page_bgr"
    start_urls = [
        'https://www.bgr.in/videos/',
        'https://www.bgr.in/videos/reviews/',
        'https://www.bgr.in/videos/news/',
        'https://www.bgr.in/videos/hands-on/',
        'https://www.bgr.in/videos/features/',
    ]
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"

    def parse(self, response):
        hxs = Selector(response)
        links = hxs.xpath("//a[@class = 'parent_alink_div']/@href").extract()
        print("BGR Started")
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        # if ("reviews" in category):
        #     category = "reviews"
        # if ("hands-on" in category):
        #     category = "gadgets"
        # if ("features" in category):
        #     category = "gadgets"
        # if ("videos" in category and len(category) == 2):
        #     category = "news"
        category = "gadgets" #all videos are phone
        print(len(links))
        for link in links:
            url = link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request

    def parse_subpage(self, response):
        try:

            global duration, video_url, url, title, description, image, video_keywords, modified_video_keywords, modified_time, category
            try:
                # duration = '0:'+response.meta['duration']
                # video_url=response.xpath('//script[contains(., "var video_file")]/text()').re('var video_file += "(.+)"')[0]

                video_url = response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl"+:+"(.+)"')[0]
                url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                duration = response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration": "(.+)"')[0]
                duration = duration.replace('PT', '0:').replace('M', ':').replace('S', '')
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords = response.xpath("//meta[@name = 'news_keywords']/@content").extract_first()
                if(video_keywords==None):
                    video_keywords=title.split()
                    video_keywords=','.join(video_keywords)
                else:
                    pass
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
                # print(modified_time)
            except:
                print("TIME ERROR")
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split(",")]
                # print(modified_video_keywords)
            except:
                print("SPLIT ERROR")
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                    "video_title": title,
                    "video_slug": slugify(title),
                    "video_link": video_url,
                    "video_description": description,
                    "broadcaster": "5eda5e4e3a51c667efdcdf88",
                    "videoformat": "5ce4f7eda5c038104cb76648",
                    "video_image": image,
                    "videokeywords": keywords,
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
            print("BGR error", err)
