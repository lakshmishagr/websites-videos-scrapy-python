from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries
from subprocess import  check_output, CalledProcessError, STDOUT

class Aajtak(scrapy.Spider):
    name="page_aajtak"
    start_urls=[

        'https://aajtak.intoday.in/videos/sports.html',
        'https://aajtak.intoday.in/videos/world.html',
        'https://aajtak.intoday.in/videos/national.html',
        'https://aajtak.intoday.in/videos/entertainment.html',
        'https://aajtak.intoday.in/videos/non-stop-100-news-videos.html',
        'https://aajtak.intoday.in/video/'
        ]
    USER_AGENT = 'Mozilla/5.0 (Android; Tablet) AppleWebKit/537.36 (KHTML, like Gecko; Android; Tablet; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/72.0.3626.121 Safari/537.36'
    def parse(self, response):
        hxs = Selector(response)
        link1 = hxs.xpath("//ul/li[@class = 'swiper-slide']/div/div/div/div/div/a/@href").extract()
        link2 = hxs.xpath("//div[@class = 'v_sld duniyaBg contenttype_1 content-video World']/a/@href").extract()
        link3 = hxs.xpath("//div[@class = 'topRightListStory content-video']/a/@href").extract()
        link4 = hxs.xpath("//div[@class = 'rightPhotoGallery content-video']/a/@href").extract()
        link5 = hxs.xpath("//div[@class = 'leftPhotoGallery content-video']/a/@href").extract()
        links=link1+link2+link3+link4+link5
        print("Aajtak Started")
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        print("\n cat",category)
        if ("sports.html" in category):
            category = "sports"
        if ("world.html" in category):
            category = "world"
        if ("national.html" in category):
            category = "news"
        if ("entertainment.html" in category):
            category = "entertainment"
        if ("non-stop-100-news-videos.html" in category):
            category = "news"
        if ("video" in category):
            category = "news"
        for link in links:
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain + link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request


    def parse_subpage(self, response):
        global video_url, duration, video_keywords, modified_video_keywords, title, description, image, modified_time, category
        print("subvalues")
        try:
            try:
                video_url = response.xpath('//script[contains(., "var jwConfig")]/text()')[0].re(".*file2.*")
                video_url= ''.join(map(str,video_url))
                video_url=video_url.replace('file2:', '')
                video_url = video_url.replace(',', '')
                video_url = video_url.replace("'", "")
                video_url = video_url.replace('', '')
                video_url = video_url.lstrip().replace('\t','').replace('\r','')
                title = response.xpath("//title/text()").extract_first()
                description = response.xpath("//meta[@name = 'description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords=response.xpath("//meta[@name = 'keywords']/@content").extract_first()
                category = response.meta['category']
                print(video_url)
                duration = None
            except:
                print("exception hit")
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
                print(duration)
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0' + time[0]
                time2 = time[1] if int(time[1]) > 9 else '0' + time[1]
                time3 = time[2]  # if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1 + ":" + time2 + ":" + time3)
                print(modified_time)
            except Exception as err:
                print("TIME ERROR", err)

            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split()]
            except:
                print("SPLIT ERROR")
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5ee0e04a87ff4b0294bdf25b",   #Not yet changed
                "videoformat" : "5ce4f7eda5c038104cb76648",   #Not yet changed
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration": modified_time,
                "category": category,
                "language": "hindi",
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }
            if ((len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8) and
                    (video_url.endswith('.mp4') or video_url.endswith('.m3u8'))):
                # print("aaa------------------aaaa")
                # print(title)
                # print(video_url)
                # print(modified_time)
                # print(image)
                # print(category)
                # print("english")
                # print(insertObject)
                # print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result.json())

        except Exception as err:
            print("Aajtak error", err)
