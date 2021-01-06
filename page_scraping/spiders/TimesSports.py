from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries
video_url = ""
modified_time = ""
class TimesSports(scrapy.Spider):
    name="page_timesSports"
    start_urls=[
        'https://timesofindia.indiatimes.com/videos/sports/cricket',
        'https://timesofindia.indiatimes.com/videos/sports/football',
        'https://timesofindia.indiatimes.com/videos/sports/tennis',
        'https://timesofindia.indiatimes.com/videos/sports/super-fight-league',
        'https://timesofindia.indiatimes.com/videos/sports/golf',
        'https://timesofindia.indiatimes.com/videos/sports/racing',
        'https://timesofindia.indiatimes.com/videos/sports/other-sports'
    ]
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        lang = "english"
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        # print(category)
        if ("cricket" in category):
            category = "sports|cricket"
        if ("football" in category):
            category = "sports|football"
        if ("tennis" in category):
            category = "sports|tennis"
        if ("super-fight-league" in category):
            category = "sports|fight"
        if ("golf" in category):
            category = "sports|golf"
        if ("racing" in category):
            category = "sports|racing"
        if("other-sports" in category ) :
            category = "sports"
        links = hxs.xpath("//figure[@class = 'D3Oi9']/a/@href").extract()
        links = links[0:5]
        print("TIMESOFINDIA Started")
        for link in links:
            # print('aaa--',link)
            url = link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            yield request
    def parse_subpage(self, response):
        print("sub_pages")
        try:
            global video_url, url, duration, video_keywords, title, description, image, modified_video_keywords, modified_time, category, lang, keywords
            try:
                video_url = response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl":"(.+)"')[0]
                split_string = video_url.split(",", 1)
                substring = split_string[0]
                video_url = substring.strip('"')
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
                category = response.meta['category']
                lang = response.meta['lang']
            except:
                print("EXCEPTION HIT")
            try:
                duration=response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration":"(.+)"')[0]
                split_string = duration.split(",", 1)
                substring = split_string[0]
                duration = substring.strip('"')
                duration = duration.replace('PT','').replace('M', ':').replace('S','')
                duration = '0:'+duration
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
                time2 = time[1] if int(time[1]) > 9 else '0'+time[1]
                time3 = time[2] if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1+":"+time2+":"+time3)
            except:
                print("ERROR")
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split()]
                keywords = Queries.insert_keywords(self, modified_video_keywords)
            except:
                print("SPLIT ERROR")

            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                 "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d3ea1293b6d5e43e2ef5998",   #Not yet changed
                "videoformat" : "5ce4f7eda5c038104cb76648",   #Not yet changed
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration" : modified_time,
                "category": category,
                "language": lang,
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }
            if ((len(video_url)>0 and len(image)>0 and len(modified_time)==8) and
                    (video_url.endswith('.mp4') or video_url.endswith('.m3u8'))) :
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