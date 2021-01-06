from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries

class EntertainmentTimesEvents(scrapy.Spider):
    name="page_entertainmenttimesEvents"
    start_urls=[
        'https://timesofindia.indiatimes.com/videos/entertainment/events/delhi',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/mumbai',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/bangalore',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/hyderabad',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/chennai',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/pune',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/ahmedabad',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/kolkata',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/lucknow',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/nagpur',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/kochi',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/jaipur',
        'https://timesofindia.indiatimes.com/videos/entertainment/events/raipur'
        ]
    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        lang = "english"
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')

        if("delhi" in category) :
            category = "events|delhi"
        if ("mumbai" in category):
            category = "events|mumbai"
        if ("bangalore" in category):
            category = "events|bangalore"
        if ("hyderabad" in category):
            category = "events|hyderabad"
        if ("chennai" in category):
            category = "events|chennai"
        if ("pune" in category):
            category = "events|pune"
        if ("ahmedabad" in category):
            category = "events|ahmedabad"
        if ("kolkata" in category):
            category = "events|kolkata"
        if ("lucknow" in category):
            category = "events|lucknow"
        if ("nagpur" in category):
            category = "events|nagpur"
        if ("kochi" in category):
            category = "events|kochi"
        if ("jaipur" in category):
            category = "events|jaipur"
        if ("raipur" in category):
            category = "events|raipur"

        links = hxs.xpath("//li[@class = 'videolistitem']/a/@href").extract()
        print("ENTERTAINMENTTIMES Started")
        links = links[0:2] #reduced to 2 for reduce un wanted updates
        for link in links:
            url = domain + link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            yield request

    def parse_subpage(self, response):
        try:
            global video_url, video_keywords, duration, title, description, image, modified_time, modified_video_keywords, lang, category
            try:
                video_url=response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl" : "(.+)"')[0]
                duration=response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration":"(.+)"')[0]
                video_keywords=response.xpath('//meta[@name = "keywords"]/@content').extract_first()
                duration = duration.replace('T','0:').replace('M', ':').replace('S','')
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                category = response.meta['category']
                lang = response.meta['lang']
            except Exception as err:
                print("times entertainment error 1  ", err)
            try:
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
                time2 = time[1] if int(time[1]) > 9 else '0'+time[1]
                time3 = time[2] if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1+":"+time2+":"+time3)
            except Exception as err:
                print("times entertainment error 2  ", err)
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split()]
            except Exception as err:
                print("times entertainment error 3  ", err)
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d3e903d3b6d5e43e2ef583c",   #Not yet changed
                "videoformat" : "5ce4f7eda5c038104cb76648",   #Not yet changed
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration" : modified_time,
                "category": category,
                "language": lang,
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }
            if (len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8) and video_url.endswith('.mp4'):
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
                    print(result)
        except Exception as err:
            print("times entertainment error 4  ",err)