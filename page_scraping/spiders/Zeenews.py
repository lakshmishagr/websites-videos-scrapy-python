from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy
import re
import json
from slugify import slugify
from ..database.Queries import Queries


def slug(string):
    return slugify(string)


class Zeenews(scrapy.Spider):
    name = 'page_zee'
    start_urls = [
        'https://zeenews.india.com/video'
    ]

    def parse(self, response):
        global links
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category[1:]
        if (category == "video"):
            links1 = hxs.xpath(
                "//div[@class='mini-video mini-video-h margin-bt30px']/a/@href").extract()
            links2 = hxs.xpath(
                "//div[@class='mini-video margin-bt10px']/a/@href").extract()
            links = links1 + links2
        # print(links)
        print("ZEENEWS Started")
        if (category == 'video'):
            category = 'news'
        for link in links:
            print("aaa",link)
            url = domain+link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request


    def parse_subpage(self, response):
        try:
            global video_url, url, duration, video_keywords, title, description, image, category, modified_time
            try:
                video_url = response.xpath(
                    "//div[@class='video-page-block pos-relative margin-bt40px']/div[@class='video-img']/div/@video-code").extract_first()
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath(
                    "//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath(
                    "//meta[@property = 'og:image']/@content").extract_first()
                article_tag = response.xpath(
                    "//meta[@property = 'article:tag']/@content").extract()
                video_keywords = ', '.join(map(str, article_tag))
                duration = response.xpath("//script[@type ='application/ld+json']/text()").re('"duration": "(.+)"')[0]
                duration = duration.replace('PT','0:').replace('M', ':').replace('S','')
                category = response.meta['category']
            except Exception as err:
                print("Zee error 1 ", err)
            try:
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
                time2 = time[1] if int(time[1]) > 9 else '0'+time[1]
                time3 = time[2] if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1+":"+time2+":"+time3)
            except Exception as err:
                print("Zee error 2 ", err)

            modified_video_keywords = [x.strip() for x in video_keywords.split()]
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d00a9632b334f16020b9f92",
                "videoformat" : "5ce4f7ffa5c038104cb76649",
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration" : modified_time,
                "category": category,
                "language": "hindi",
                "keywords": ' | '.join(map(str, modified_video_keywords))
                }
            if (len(video_url)>0 and len(image)>0 and len(modified_time)==8) :
                # print("aaa------------------aaaa")
                # print(modified_video_keywords)
                # print(' | '.join(map(str, modified_video_keywords)) )
                # print(title)
                # print(video_url)
                # print(modified_time)
                # print(image)
                # print(category)
                # print("hindi")
                # print(insertObject)
                # print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result)

        except Exception as err:
            print("Zee error 3  ",err)
