from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries
from subprocess import  check_output, CalledProcessError, STDOUT 

class IndiaCom(scrapy.Spider):
    name="page_indiacom"
    start_urls=[
        'https://www.india.com/video-gallery/',
        # 'https://www.india.com/video-gallery/page/2/',
        # 'https://www.india.com/video-gallery/page/3/',
        # 'https://www.india.com/video-gallery/page/4/',
        'https://www.india.com/lifestyle/videos/'
        ]
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
    def parse(self, response):
        hxs = Selector(response)
        links = hxs.xpath("//li[@class = 'catPgListitem']/figure/a/@href").extract()
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        if ("video-gallery" in category):
            category = "news"
        if('lifestyle' in category):
            category = "lifestyle"
        print("INDIACOM Started")
        print(len(links))
        for link in links:
            url = link
            print(link)
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request
    def parse_subpage(self, response):
        global video_url, url, title, description,duration, image, video_url, video_keywords, modified_time, modified_video_keywords, category
        try:
            try:
                video_url = response.xpath('//script[@type = "application/ld+json"]/text()').re('"contentUrl"+: +"(.+)"')[0]
                url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
                category = response.meta['category']
                # dd = response.xpath("//span[@class='vjs-duration-display']").extract()
                # print("aaa",dd)
                duration = response.xpath("//meta[@property = 'video:duration']/@content").extract_first()
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

            except Exception as err:
                print("EXCEPTION HIT",err)

            try:
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
                time2 = time[1] if int(time[1]) > 9 else '0'+time[1]
                time3 = time[2] #if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1+":"+time2+":"+time3)

            except Exception as err:
                print("TIME ERROR",err)

            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split()]
            except Exception as err:
                print("SPLIT ERROR",err)
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
                "broadcaster" : "5d1ef40f43eefdb023bf9d84",
                "videoformat" : "5ce4f7eda5c038104cb76648",
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration" : modified_time,
                "category": category,
                "language": "english",
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }
            if ((len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8) and video_url.startswith('http') and
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
            print("indiacom error", err)
