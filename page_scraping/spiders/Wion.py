from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries


class Wion(scrapy.Spider):
    name="page_wion"
    start_urls=[
            'https://www.wionews.com/south-asia',
            'https://www.wionews.com/world',
            'https://www.wionews.com/business-economy',
            'https://www.wionews.com/sports',
            'https://www.wionews.com/entertainment',
            'https://www.wionews.com/opinions',
            'https://www.wionews.com/videos'
            ]
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category[1:]
        if(category == "videos") :
            links1 = hxs.xpath("//div[@class='media-holder new-play-icon']/a/@href").extract()
            times1 = hxs.xpath("//div[@class = 'media-holder new-play-icon']/div/span/span/text()").extract()
            links2 = hxs.xpath("//div[@class='new-widget-type-view-2 rwd-based clearfix']/div/div/div/a/@href").extract()
            times2 = hxs.xpath("//div[@class = 'new-widget-type-view-2 rwd-based clearfix']/div/div/span/text()").extract()
            links4 = hxs.xpath("//div[@class='new-widget-type-view-5 mbl-view clearfix']/div/div/a/@href").extract()
            times4 = hxs.xpath("//div[@class = 'new-widget-type-view-5 mbl-view clearfix']/div/div/span/text()").extract()
            links = links1 + links2 + links4
            times = times1 + times2 + times4
        else:
            #after this delete 4 videos, bcoz its ad videos, if its main page /videos
            links3 = hxs.xpath("//div[@class='new-widget-type-view-5 mbl-view clearfix']/div/div/div/a/@href").extract()
            times3 = hxs.xpath("//div[@class = 'new-widget-type-view-5 mbl-view clearfix']/div/div/span/text()").extract()
            # links3 = links3[0 :len(links3)-4]
            # times3 = times3[0 : len(times3)-4]
            links = links3
            times = times3

        print ("WION Started")
        for link, duration in zip(links, times):
            # print("aaaa",link)
            # print("bbbb",duration)
            if(category == "south-asia"):
                category = 'world'
            if (category == "business-economy"):
                category = 'business'
            if (category == "sports"):
                category = 'sports'
            if (category == "entertainment"):
                category = 'entertainment'
            if (category == "world"):
                category = 'world'
            if (category == 'videos'):
                category = 'news'
            if (category == "opinions"):
                category = 'opinions'

            url = domain+link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['duration'] = duration
            request.meta['category'] = category
            yield request
    def parse_subpage(self, response):
        try:
            global video_url, url, duration, category, video_keywords, title, description, image, modified_video_keywords, modified_time, keywords
            try:
                video_url=response.xpath('//script[contains(., "var vtype")]/text()').re('video_url = \'(.+)\'')[0]
                duration = response.meta['duration']
                url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                img = image.split(',')
                image = img[0]
                video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
                category = response.meta['category']
            except Exception as err:
                print("Error  ",err)
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split(",")]
                # keywords = Queries.insert_keywords(self, modified_video_keywords)
            except Exception as err:
                print("Error  ",err)

            insertObject = {
                "video_title" : title,
                # "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d1c58b2f27ebc4b8706fd10",
                "videoformat" : "5ce4f7ffa5c038104cb76649",
                "video_image" : image,
                # "videokeywords" : keywords,
                "page_url": response.url,
                "duration" : duration,
                "category" : category,
                "language" : "english",
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }
            if (( len(video_url) >0 and len(image) >0 and len(duration) == 8) and
                    (video_url.endswith('.mp4') or video_url.endswith('.m3u8'))) :
                print("aaa------------------aaaa")
                print(title)
                print(video_url)
                print(duration)
                print(image)
                print(category)
                print("english")
                # print(insertObject)
                print("bbb--------------------bbb")
                # result = Queries.insert_api(self, insertObject)
                # if result.status_code == 200:
                #     print("INSERTED")
                # else:
                #     print(result.status_code)
                #     print(result)
        except Exception as err:
            print("Error  ",err)
