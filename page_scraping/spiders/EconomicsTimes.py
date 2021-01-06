from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html
from slugify import slugify
from ..database.Queries import Queries

class EconomicsTimes(scrapy.Spider):
    name='page_economicstimes'
    start_urls=[
        # 'https://economictimes.indiatimes.com/et-now/et-now-live', #no need main page all get in latest videos
        'https://economictimes.indiatimes.com/et-now/stocks',
    ]

    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = "economics"
        lang = "english"

        # links = hxs.xpath("//div[@class='thumb']/a/@href").extract() #its main page all videos, No need
        links = hxs.xpath("//ul[@class='flt']/li/a/@href").extract()
        print(len(links))
        print("ECONOMICSTIMES STARTED")
        for link in links:
            print("aaa--",link)
            url = domain + link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            yield request

    def parse_subpage(self, response):
        hxs = Selector(response)
        try:
            global modified_time, modified_keywords, video_url, video_keywords, description, image, duration, title, time2, time3, category, lang
            try:
                video_url = response.xpath("//meta[@itemprop = 'contentUrl']/@content").extract_first()
                title = hxs.xpath("//meta[@property = 'og:title']/@content").extract_first()
                video_keywords = hxs.xpath("//meta[@name ='keywords']/@content").extract_first()
                description = hxs.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = hxs.xpath("//meta[@property = 'og:image']/@content").extract_first()
                duration=response.xpath("//meta[@itemprop = 'duration']/@content").extract_first()
                duration = duration.replace('T','0:').replace('M', ':').replace('S','')
                category = response.meta['category']
                lang = response.meta['lang']
            except:
                print("EXCEPTION HIT")
            try:
                modified_keywords = [x.strip() for x in video_keywords.split(',')]
            except:
                print("SPLIT ERROR")
            try:
                time = duration.split(':')
                if(len(time[0]) < 2):
                    time[0] = '0' + time[0]
                if(len(time[1]) < 2):
                    time[1] = '0' + time[1]
                if (len(time[2]) < 2):
                    time[2] = '0' + time[2]
                modified_time = str(time[0] + ":" + time[1] + ":" + time[2])
            except:
                print("TIME ERROR")

            keywords = Queries.insert_keywords(self, modified_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d3e8c693b6d5e43e2ef583b",   #Not changed yet
                "videoformat" : "5ce4f7eda5c038104cb76648",   #Not changed yet
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration" : modified_time,
                "category": category,
                "language": lang,
                "keywords": ' | '.join(map(str, modified_keywords))
            }
            if (len(video_url) > 0 and len(image) > 0 and len(modified_time)==8) and video_url.endswith('.mp4'):
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
        except:
            print("URL MISSING")
