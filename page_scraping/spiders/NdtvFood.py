from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries

class NdtvFood(scrapy.Spider):
    name="page_ndtvfood"
    start_urls=[
        'https://food.ndtv.com/videos',
        'https://food.ndtv.com/videos/page-2',
        ]
    # Rules = (Rule(LinkExtractor(allow=(), restrict_xpaths=('//a[@rel="next"]',)), callback="parse", follow=True),)
    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = "food"
        lang = 'english'
        # next_page = hxs.xpath("//a[@rel='next']/@href").get()  #comments are old code preserved
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parse)
        # for link in links2:
        #     url = link
        #     yield scrapy.Request(url, callback=self.parse_subpage)
        # if next_page:
        #     next_href = next_page[0]
        #     next_page_url = 'https://food.ndtv.com/videos' + next_href
        #     links2 = scrapy.Request(url=next_page_url)
        #     print(links2)

        links = hxs.xpath("//div[@class = 'vdo_img_cont']/a/@href").extract()
        # links = links[0:5]
        for link in links:
            # print("aaa--",link)
            url = link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            yield request

        # yield scrapy.Request(next_page, callback=self.parse)
        # print("\nlinks2222", next_page)
        # for link in links2:
        #     url = link
        #     yield scrapy.Request(url, callback=self.parse_subpage)
    def parse_subpage(self, response):
        try:
            global video_url, url, duration, video_keywords, title, description, image, modified_video_keywords, modified_time, category, lang
            try:
                url=response.xpath('//script[contains(., "var __html5playerdata")]/text()').re('"media_mp4":"(.+)"')[0]
                video = url.split('","')
                video_url = video[0].replace('\\', '')
                url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
                duration = response.xpath("//meta[@itemprop = 'duration']/@content").extract_first()
                duration = duration.replace('PT','0:').replace('M', ':').replace('S','')
                # yield {
                #     'food':response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                # }
                category = response.meta['category']
                lang = response.meta['lang']
            except Exception as err:
                print("EXCEPTION HIT",err)
            try:
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
                time2 = time[1] if int(time[1]) > 9 else '0'+time[1]
                time3 = time[2] if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1+":"+time2+":"+time3)
            except Exception as err:
                print("Modified time ERROR",err)
            # global modified_video_keywords
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split()]

            except Exception as err:
                print("Split Error",err)
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d3e9bfe3b6d5e43e2ef58e9",   #Not yet changed
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
                # # print(insertObject)
                # print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result)
        except Exception as err:
            print("URL MISSING",err)
