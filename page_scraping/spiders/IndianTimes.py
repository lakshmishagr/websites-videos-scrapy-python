from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries
from subprocess import  check_output, CalledProcessError, STDOUT 

class IndianTimes(scrapy.Spider):
    name="page_indiantimes"
    start_urls=[
        'https://www.indiatimes.com/videos/people/',
        'https://www.indiatimes.com/videos/news-that-matters/',
        'https://www.indiatimes.com/videos/wtf/',
        'https://www.indiatimes.com/videos/human-interest/',
        'https://www.indiatimes.com/videos/pollution/',
        'https://www.indiatimes.com/videos/india/',
        'https://www.indiatimes.com/videos/space/',
        'https://www.indiatimes.com/videos/sports/',
        'https://www.indiatimes.com/videos/urban-mobility/',
        'https://www.indiatimes.com/videos/science/',
        'https://www.indiatimes.com/videos/global-warming/',
        'https://www.indiatimes.com/videos/kangchenjunga-calling/'
        ]
    USER_AGENT = 'Mozilla/5.0 (Android; Tablet) AppleWebKit/537.36 (KHTML, like Gecko; Android; Tablet; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/72.0.3626.121 Safari/537.36'
    def parse(self, response):
        hxs = Selector(response)
        # links = hxs.xpath("//div[@class = 'video-cont mb-20']/div/a/@href").extract()
        links = hxs.xpath("//div[@class = 'card small-video-card ']/div/a/@href").extract()
        print("INDIATIMES Started")
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        if ("people" in category):
            category = "news"
        if ("news-that-matters" in category):
            category = "news"
        if ("wtf" in category):
            category = "news"
        if ("human-interest" in category):
            category = "news"
        if ("pollution" in category):
            category = "environment"
        if ("india" in category):
            category = "news"
        if ("space" in category):
            category = "science"
        if ("sports" in category):
            category = "sports"
        if ("urban-mobility" in category):
            category = "news"
        if ("science" in category):
            category = "science"
        if ("global-warming" in category):
            category = "environment"
        if ("kangchenjunga-calling" in category):
            category = "travel"
        if ("videos" in category and len(category) == 2):
            category = "news"
        # links = links[0:1]
        for link in links:
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain + link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request

    def parse_subpage(self, response):
        global title, video_url, description, image, modified_time, category, duration, video_keywords, modified_video_keywords
        print("subvalues")
        try:

            try:
                video_url =response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl"+:+ "(.+)"')[0]
                video_url=video_url.replace("//slike.","slike.")
                duration1 = response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration"+:+ "(.+)"')[0]
                duration = duration1.replace('T', '0:').replace('M', ':').replace('S', '')
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords=response.xpath("//meta[@name = 'keywords']/@content").extract_first()
                category = response.meta['category']

            except:
                print("exception hit")
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
                print("ERROR")
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
                "duration": modified_time,
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
            print("indiantimes error", err)
