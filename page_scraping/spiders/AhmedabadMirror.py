from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries

class AhmedabadMirror(scrapy.Spider):
    name="page_ahmedabadmirror"
    start_urls=[
        'https://ahmedabadmirror.indiatimes.com/videos/videolist/msid-3812907,more-1.cms',
        'https://ahmedabadmirror.indiatimes.com/videos/videolist/msid-4928483,more-1.cms',
        'https://ahmedabadmirror.indiatimes.com/videos/videolist/msid-36747721,more-1.cms',
        'https://ahmedabadmirror.indiatimes.com/videos/videolist/msid-3813456,more-1.cms',
        'https://ahmedabadmirror.indiatimes.com/videos/lifestyle',
        'https://ahmedabadmirror.indiatimes.com/videos/business',
        'https://ahmedabadmirror.indiatimes.com/videos/funny',
        'https://ahmedabadmirror.indiatimes.com/videos/celebs',
        'https://ahmedabadmirror.indiatimes.com/videos',
        ]
    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        if ("msid-3812907,more-1.cms" in category):
            category = "news"
        if ("msid-4928483,more-1.cms" in category):
            category = "entertainment"
        if ("msid-36747721,more-1.cms" in category):
            category = "entertainment|movies"
        if ("lifestyle" in category):
            category = "lifestyle"
        if ("business" in category):
            category = "business"
        if ("funny" in category):
            category = "funny"
        if ("msid-3813456,more-1.cms" in category):
            category = "sports"
        if ("celebs" in category):
            category = "celebrity"
        if ("videos" in category and len(category) == 2):
            category = "news"

        print("AhmedabadMirror Started")
        links = hxs.xpath("//li[@class = 'featuredLi']/span/a/@href").extract()
        print(len(links))
        # links = links[0:1]
        for link in links:
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain + link
            # print("aaa--",url)
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request

    def parse_subpage(self, response):
        global video_url, duration, video_keywords, duration, title, description, image,modified_time, category
        try:
            try:
                video_url=response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl":"(.+)"')[0]
                if (video_url == None or video_url == ""):
                    print("video url None")
                    raise Exception("its not video url")
                else:
                    pass
                duration=response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration":"(.+)"')[0]
                video_keywords=response.xpath('//script[@type = "application/ld+json"]/text()').re('"keywords":"(.+)"')
                video_keywords = ', '.join(map(str, video_keywords))
                duration = duration.replace('T','0:').replace('M', ':').replace('S','')
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@name='description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                category = response.meta['category']
            except:
                print("EXCEPTION HIT")
            try:
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
                time2 = time[1] if int(time[1]) > 9 else '0'+time[1]
                time3 = time[2] #if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1+":"+time2+":"+time3)
                # print(modified_time)

            except:
                print("TIME ERROR")
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split()]
                # print(modified_video_keywords)
                # print(description)
                keywords = Queries.insert_keywords(self, modified_video_keywords)
            except:
                print("SPLIT Error")
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d3daf604af5fc1499b9c627",   #Not yet changed
                "videoformat" : "5ce4f7eda5c038104cb76648",   #Not yet changed
                "video_image" : image,
                "videokeywords" : keywords,
                "url": response.url,
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
                # print(description)
                # # print(insertObject)
                # print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result.json())

        except Exception as err:
            print("url error", err)
