from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries
from subprocess import  check_output, CalledProcessError, STDOUT

class TheHealthSite(scrapy.Spider):
    name="page_healthsite"
    start_urls=[
        'https://www.thehealthsite.com/video-gallery/',
        'https://www.thehealthsite.com/video-gallery/page/2/',
        'https://www.thehealthsite.com/video-gallery/page/3/',
        'https://www.thehealthsite.com/video-gallery/page/4/',
        ]
    def parse(self, response):
        hxs = Selector(response)
        category = "health"
        lang = 'english'
        links = hxs.xpath("//h3[@style = 'overflow: hidden;']/a/@href").extract()
        # print("\nlinkd",links)
        for link in links:
            # print("aaa--",link)
            url = link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            yield request

    def parse_subpage(self, response):
        print("\nsubvalues\n")
        try:
            global video_url, url, duration, video_keywords, title, description, image, modified_video_keywords, modified_time, category, lang
            try:
                video_url =response.xpath('//script[contains(., "var video_file")]/text()').re('var video_file += "(.+)"')[0]
                url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                if(image==None):
                    image = response.xpath("//meta[@name = 'twitter:image']/@content").extract_first()
                else:
                    pass
                video_keywords = response.xpath("//meta[@name = 'news_keywords']/@content").extract_first()
                category = response.meta['category']
                lang = response.meta['lang']
                duration = None

            except Exception as err:
                print("EXCEPTION HIT",err)
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

            try:
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0' + time[0]
                time2 = time[1] if int(time[1]) > 9 else '0' + time[1]
                time3 = time[2]  # if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1 + ":" + time2 + ":" + time3)

            except Exception as err:
                print("TIME ERROR", err)

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
                "broadcaster" : "5edf3a99820f925d307ae316",   #Not yet changed
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
            print("HealthSite",err)
