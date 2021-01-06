from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json, sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries


class MissKyra(scrapy.Spider):
    name = "page_misskyra"
    start_urls = [
        'https://www.misskyra.com/videolist.cms'
    ]

    def parse(self, response):
        hxs = Selector(response)
        links1 = hxs.xpath("//ul[@class = 'videos_listing']/li/a/@href").extract()
        links2 = hxs.xpath("//section[@class='fix_wrapper midtop_section']/ul/li/a/@href").extract()

        print("MISSKYRA Started")
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        category = 'celebrity'
        links = links2 + links1

        for link in links:
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain + link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request


    def parse_subpage(self, response):
        try:
            global video_url, duration, title, description, image, video_keywords, modified_time, modified_video_keywords, category
            print("subvalues")
            try:
                video_url = response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl":"(.+)"')[0]
                duration = response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration":"(.+)"')[0]
                video_keywords = response.xpath('//script[@type = "application/ld+json"]/text()').re('"keywords":"(.+)"')[0]
                duration = duration.replace('T', '0:').replace('M', ':').replace('S', '')
                title = response.xpath("//title/text()").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                category = response.meta['category']
            except:
                print("EXCEPTION HIT")
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
                print("TiME ERROR")
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split()]

            except:
                print("SPLIT ERROR")
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title": title,
                "video_slug": slugify(title),
                "video_link": video_url,
                "video_description": description,
                "broadcaster": "5d3e98123b6d5e43e2ef58e4",  # Not yet changed
                "videoformat": "5ce4f7eda5c038104cb76648",  # Not yet changed
                "video_image": image,
                "videokeywords": keywords,
                "page_url": response.url,
                "duration": modified_time,
                "category": category,
                "language": "english",
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }

            if ((len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8) and (video_url.endswith('.mp4') or video_url.endswith('.m3u8'))):
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
            print("misskyra error", err)
