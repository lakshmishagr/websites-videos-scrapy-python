from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json, sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries

from subprocess import  check_output, CalledProcessError, STDOUT 

class Dna(scrapy.Spider):
    name = "page_dna"
    start_urls = [
        'https://www.dnaindia.com/entertainment',
        'https://www.dnaindia.com/sports',
        'https://www.dnaindia.com/world',
        'https://www.dnaindia.com/business',
        'https://www.dnaindia.com/technology',
        'https://www.dnaindia.com/lifestyle',
        'https://www.dnaindia.com/videos',
    ]
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
    def parse(self, response):
        hxs = Selector(response)
        print("DNA Started")
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        print("\n",category)
        if ("entertainment" in category):
            category = "entertainment"
        if ("sports" in category):
            category = "sports"
        if ("world" in category):
            category = "world"
        if ("business" in category):
            category = "business"
        if ("technology" in category):
            category = "technology"
        if ("lifestyle" in category):
            category = "lifestyle"
        if ("videos" in category):
            category = "news"
            # links1 = hxs.xpath("//div[@class = 'vidcol4']/div/span/div/a/@href").extract()
            # links2 = hxs.xpath("//div[@data-min-enable = 'section fronts']/a/@href").extract()
            links3 = hxs.xpath("//div[@class ='videolandtprgtpsrl']/a/@href").extract()
            links4 = hxs.xpath("//div[@class ='videolandtplft']/a/@href").extract()
            links5 = hxs.xpath("//div[@class ='bollydwnslider']/a/@href").extract()
            links = links3 +links4 + links5
        else:
            links6 = hxs.xpath("//div[@class='col-lg-3 col-md-3']/a/@href").extract()
            links = links6

        # links=links[0:2]
        for link in links:
            url = domain + link
            print("aaa--",url)
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request
    def parse_subpage(self, response):
        try:
            global url, video_url, title, description, image, video_keywords, duration, modified_time, category
            try:
                # url=response.xpath("//script[contains(., 'file:')]/text()").re_first("file(?:local)?:(.+),")[0]
                video_url=response.xpath("//div[@class = 'gldetlfltbxdwn']/div/div/@video-code").extract_first()
                # video_url = video_url1.replace("/index.m3u8", "")
                url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords = response.xpath("//meta[@name = 'news_keywords']/@content").extract_first()
                category = response.meta['category']
                duration = response.xpath("//meta[@property = 'video:duration']/@content").extract_first()
                # print(title)
                # print(video_url)
                # # print(modified_time)
                # print(image)
                # print(category)
                print('cc',duration)

                command = [
                    'ffprobe',
                    '-v',
                    'error',
                    '-show_entries',
                    'format=duration',
                    '-of',
                    'default=noprint_wrappers=1:nokey=1',
                    video_url
                ]

                if (duration == None):
                    output = check_output(command, stderr=STDOUT).decode()
                    duration = round(float(output) / 60, 2)
                    duration = str(duration).replace('.', ':')
                    duration = '0:' + duration
                else:
                    duration = round(float(duration) / 60, 2)
                    duration = str(duration).replace('.', ':')
                    duration = '0:' + duration
                print('dd',duration)
            except Exception as err:
                print("EXCEPTION HIT",err)

            try:
                time = duration.split(':')
                if (len(time[0]) < 2):
                    time[0] = '0' + time[0]
                if (len(time[1]) < 2):
                    time[1] = '0' + time[1]
                if (len(time[2]) < 2):
                    time[2] = '0' + time[2]
                modified_time = str(time[0] + ":" + time[1] + ":" + time[2])
                print(modified_time)
            except Exception as err:
                print("ERROR",err)
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split(",")]
            except Exception as err:
                print("modified keyword error",err)

            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                    "video_title": title,
                    "video_slug": slugify(title),
                    "video_link": video_url,
                    "video_description": description,
                    "broadcaster": "5d246eded106ef35f2d72710",  #Not yet changed
                    "videoformat": "5ce4f7ffa5c038104cb76649",  #Not yet changed
                    "video_image": image,
                    "videokeywords": keywords,
                    "page_url": response.url,
                    "duration" : modified_time,
                    "category": category,
                    "language": "english",
                    "keywords": ' | '.join(map(str, modified_video_keywords))
                }
            if ((len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8) and
                    (video_url.endswith('.mp4') or video_url.endswith('.m3u8'))):
                print("aaa------------------aaaa")
                print(title)
                print(video_url)
                print(modified_time)
                print(image)
                print(category)
                print("english")
                # print(insertObject)
                print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result.json())
        except Exception as err:
            print("DNA error", err)

