from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries

class EntertainmentTimesMusic(scrapy.Spider):
    name="page_entertainmenttimesMusic"
    start_urls=[
        'https://timesofindia.indiatimes.com/videos/entertainment/music/hindi',
        'https://timesofindia.indiatimes.com/videos/entertainment/music/kannada',
        'https://timesofindia.indiatimes.com/videos/entertainment/music/english',
        'https://timesofindia.indiatimes.com/videos/entertainment/music/tamil',
        'https://timesofindia.indiatimes.com/videos/entertainment/music/telugu',
        'https://timesofindia.indiatimes.com/videos/entertainment/music/malayalam',
        'https://timesofindia.indiatimes.com/videos/entertainment/music/bengali',
        'https://timesofindia.indiatimes.com/videos/entertainment/music/punjabi',
        'https://timesofindia.indiatimes.com/videos/entertainment/music/marathi',
        'https://timesofindia.indiatimes.com/videos/entertainment/music/gujarati',
        'https://timesofindia.indiatimes.com/videos/entertainment/music/bhojpuri',
        'https://timesofindia.indiatimes.com/videos/entertainment/music/haryanvi'
        ]
    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = "entertainment|Music"
        lang = '{uri.path}'.format(uri=parsed_uri)
        lang = lang.split('/')
        print(lang)
        if("hindi" in lang) :
            lang = "hindi"
        if ("kannada" in lang):
            lang = "kannada"
        if ("hollywood" in lang):
            lang = "english"
        if ("tamil" in lang):
            lang = "tamil"
        if ("telugu" in lang):
            lang = "telugu"
        if ("telugu" in lang):
            lang = "telugu"
        if ("malayalam" in lang):
            lang = "malayalam"
        if ("bengali" in lang):
            lang = "bengali"
        if ("marathi" in lang):
            lang = "marathi"
        if ("gujarati" in lang):
            lang = "gujarati"
        if ("bhojpuri" in lang):
            lang = "bhojpuri"
        if ("punjabi" in lang):
            lang = "punjabi"
        if ("haryanvi" in lang):
            lang = "haryanvi"

        links = hxs.xpath("//li[@class = 'videolistitem']/a/@href").extract()
        print("ENTERTAINMENTTIMES Started")
        links = links[0:5] #reduced to 5 for reduce un wanted updates
        # print('qqqqqqq--',len(links))
        for link in links:
            # print("aaaaa-",link)
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
            if (len(video_url)>0 and len(image)>0 and len(modified_time)==8) and video_url.endswith('.mp4') :
                # print("aaa------------------aaaa")
                # print(title)
                # print(video_url)
                # print(modified_time)
                # print(image)
                # print(category)
                # print(lang)
                # print(insertObject)
                # print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result)
        except Exception as err:
            print("times entertainment error 4  ",err)