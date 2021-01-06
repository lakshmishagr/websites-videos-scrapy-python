from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries

class NdtvDoctor(scrapy.Spider):
    name="page_ndtvdoctor"
    start_urls=[
        'https://doctor.ndtv.com/videos',
        ]

    def parse(self, response):
        self.y_count = 0
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = "health"
        lang = 'english'
        links = hxs.xpath("//div[@class = 'left-stry-pic']/a/@href").extract()
        print("NDTV DOCTOR Started")
        for link in links:
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain + link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            yield request

    def parse_subpage(self, response):
        print("subvalues")
        self.y_count += 1
        try:
            global video_url, duration, video_keywords,url, title, description, image, modified_video_keywords, modified_time, category, lang
            try:
                video_url=response.xpath('//script[contains(., "var __html5playerdata")]/text()').re('"media_mp4": "(.+)"')[0]
                url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
                duration = response.xpath("//div[@class = 'story_timing']/span/text()").extract_first().replace(' Min', '')
                category = response.meta['category']
                lang = response.meta['lang']
            except:
                print("EXCEPTION HIT")
            # print("\n tot", title.y_count)
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split()]
            except:
                print("SPLIT ERROR")
            duration = '0:'+duration
            try:
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
                time2 = time[1] #if int(time[1]) > 9 else '0'+time[1]
                time3 = time[2] #if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1+":"+time2+":"+time3)

            except:
                print("TIME ERROR")
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d3e9b833b6d5e43e2ef58e8",   #Not yet changed
                "videoformat" : "5ce4f7eda5c038104cb76648",   #Not yet changed
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration" : modified_time,
                "category": category,
                "language": lang,
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }
            if ((len(video_url)>0 and len(image)>0 and len(modified_time)==8)
                    and ( video_url.endswith('.m3u8') or video_url.endswith('.mp4'))) :
                # print("aaa------------------aaaa")
                # print(title)
                # print(video_url)
                # print(modified_time)
                # print(image)
                # print(category)
                # print(lang)
                # # # print(insertObject)
                # print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result)
        except:
            print("URL MISSING")