from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries
count=0

class BangaloreMirror(scrapy.Spider):
    name="page_bangaloremirror"
    start_urls=[
        'https://bangaloremirror.indiatimes.com/videos/business',
        'https://bangaloremirror.indiatimes.com/videos/news',
        'https://bangaloremirror.indiatimes.com/videos/entertainment',
        'https://bangaloremirror.indiatimes.com/videos/sports',
        'https://bangaloremirror.indiatimes.com/videos/lifestyle',
        'https://bangaloremirror.indiatimes.com/videos/funny',
        'https://bangaloremirror.indiatimes.com/videos/celebs',
        'https://bangaloremirror.indiatimes.com/videos/',
        ]
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"

    def parse(self, response):
        hxs = Selector(response)
        links = hxs.xpath("//li[@class = 'featuredLi']/span/a/@href").extract()
        print("BangaloreMirror Started")
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        # print(category)
        if ("entertainment" in category):
            category = "entertainment"
        if ("movies" in category):
            category = "entertainment"
        if ("business" in category):
            category = "business"
        if ("sports" in category):
            category = "sports"
        if ("lifestyle" in category):
            category = "lifestyle"
        if ("news" in category):
            category = "news"
        if ("celebs" in category):
            category = "celebrities"
        if ("funny" in category):
            category = "funny"
        if ("latest" in category):
            category = "news"
        if ("videos" in category and len(category) == 2):
            category = "news"
            links=links[0:40]
        else:
            links = links[0:5] #links reduced to 5 to reduce time of unwanted

        print(category)
        for link in links:
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain + link
            # yield scrapy.Request(url, callback=self.parse_subpage)
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request

    def parse_subpage(self, response):
        try:
            global video_url, duration, video_keywords, title, description, image, modified_time, category
            try:
                video_url=response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl"+:+"(.+)"')[0]
                # print(video_url)
                # video_url=response.xpath("//meta[@property = 'og:url']/@content").extract_first()
                # if (video_url.endswith(".cms")):
                #     print("CMS Found")
                #     raise Exception("its not video url")
                # else:
                #     pass
                duration=response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration":"(.+)"')[0]
                video_keywords=response.xpath('//script[@type = "application/ld+json"]/text()').re('"keywords":"(.+)"')[0]
                duration = duration.replace('T','0:').replace('M', ':').replace('S','')
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                category = response.meta['category']
            except Exception as err:
                print("EXCEPTITON HIT",err)
            try:
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
                time2 = time[1] if int(time[1]) > 9 else '0'+time[1]
                time3 = time[2] if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1+":"+time2+":"+time3)

            except:
                print("TIME ERROR")
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split()]

            except:
                print("SPLIT ERROR")
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d3e8b5d3b6d5e43e2ef583a",   #Not yet changed
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
                    (video_url.endswith('.mp4') or video_url.endswith('.m3u8'))) :
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
            print("Bangalore error",err)
