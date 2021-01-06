from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries

class iDiva(scrapy.Spider):
    name="page_idiva"
    start_urls=[
        'https://www.idiva.com/videos/feed/',
        'https://www.idiva.com/videos/feed/2',
        'https://www.idiva.com/videos/feed/3',
        'https://www.idiva.com/videos/feed/4',

        ]
    # user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
    def parse(self, response):
        hxs = Selector(response)
        # print("hhhxxxsss",hxs)
        links = hxs.xpath("//a[@class = 'line-none embed-responsive-2by3']/@href").extract()
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        if ("videos" in category):
            category = "entertainment"

        for link in links:
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain + link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request

    def parse_subpage(self, response):
        global title, video_keywords, video_url, description, image, category, modified_time, modified_video_keywords
        try:
            try:
                print("subvalues")
                video_url=response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl": "(.+)"')[0]
                video_url=video_url.replace("//","")
                duration=response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration": "(.+)"')[0]
                video_keywords=response.xpath('//script[@type = "application/ld+json"]/text()').re('"keywords" : "(.+)"')
                video_keywords = ', '.join(map(str, video_keywords))
                duration = duration.replace('T','0:').replace('M',':').replace('S','')
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                if(title==None):
                    title = response.xpath("//title/text()").extract_first()
                else:
                    pass
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                category = response.meta['category']
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
            except Exception as err:
                print("EXCEPTITON HIT",err)
            try:
                time = duration.split(':')
                if (len(time[0]) < 2):
                    time[0] = '0' + time[0]
                if (len(time[1]) < 2):
                    time[1] = '0' + time[1]
                if (len(time[2]) < 2):
                    time[2] = '0' + time[2]
                modified_time = str(time[0] + ":" + time[1] + ":" + time[2])
                print(modified_time)
            except:
                print("TIME ERROR")
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split()]
            except:
                print("SPLIT ERROR")
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            if video_url.startswith('slike-v.akamaized.net'):
                video_url = "https://"+ video_url
            if video_url.startswith('//vslike.akamaized.net'):
                video_url = "https:"+ video_url
            if video_url.startswith('//slike-v.akamaized.net'):
                video_url = "https:"+ video_url

            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d1ef40f43eefdb023bf9d84",   #Not yet changed
                "videoformat" : "5ce4f7eda5c038104cb76648",   #Not yet changed
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration": duration,
                "category": category,
                "language": "english",
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }

            if ((len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8) and video_url.startswith('http') and 
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
            print("IDIVA error", err)
