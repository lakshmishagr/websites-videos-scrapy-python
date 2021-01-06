from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from subprocess import  check_output, CalledProcessError, STDOUT
from ..database.Queries import Queries

class HT(scrapy.Spider):
    name="page_HT"
    start_urls=[
        'https://www.hindustantimes.com/videos/coronavirus-crisis/',
        'https://www.hindustantimes.com/videos/on-the-record/',
        'https://www.hindustantimes.com/videos/aurbatao/',
        'https://www.hindustantimes.com/videos/movie-reviews/',
        'https://www.hindustantimes.com/videos/entertainment/',
        'https://www.hindustantimes.com/videos/your-weekend-dose/',
        'https://www.hindustantimes.com/videos/worldview/',
        'https://www.hindustantimes.com/videos/sports-corner/',
        'https://www.hindustantimes.com/videos/sports/',
        'https://www.hindustantimes.com/videos/world/',
        'https://www.hindustantimes.com/videos/',
        ]

    # user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        lang = "english"
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        # print(category)
        if ("coronavirus-crisis" in category):
            category = "news"
        if ("on-the-record" in category):
            category = "opinions"
        if ("aurbatao" in category):
            category = "entertainment"
        if ("movie-reviews" in category):
            category = "entertainment|movies"
        if ("entertainment" in category):
            category = "entertainment"
        if ("your-weekend-dose" in category):
            category = "entertainment"
        if("worldview" in category ) :
            category = "world"
        if ("sports-corner" in category):
            category = "sports"
        if ("sports" in category):
            category = "sports"
        if ("world" in category):
            category = "world"
        if("videos" in category and len(category) ==3):
            category = "news"

        links = hxs.xpath("//div[@class = 'videoinfo-video']/h3/a/@href").extract()
        print(len(links))
        print("HT Started")
        links = links[0:20]
        for link in links:
            url = link
            # print("aaa--",url)
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            yield request


    def parse_subpage(self, response):
        print("Not Working")
        try:
            global video_url, url, duration, title, description, image, video_keywords, modified_time, modified_video_keywords, category, lang
            try:
                category = response.meta['category']
                lang = response.meta['lang']
                video_url = response.xpath("//meta[@itemprop = 'contentUrl']/@content").extract_first()
                duration = response.xpath("//meta[@itemprop = 'duration']/@content").extract_first()
                # duration = duration.replace('PT', '').replace('M', ':').replace('S', '')
                # print ("\n duration \n", duration)
                title = response.xpath("//meta[@itemprop = 'name']/@content").extract_first()
                description = response.xpath("//meta[@itemprop = 'description']/@content").extract_first()
                image = response.xpath("//meta[@itemprop = 'thumbnailUrl']/@content").extract_first()
                video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
                # print('aaa----------------aaa')
                # print(duration)
                # print(duration.find('.'))
                dotremover = duration.find('.')
                duration = duration[0:dotremover].replace('PT','0:').replace('M',':').replace('S','')

                # command = [
                #     'ffprobe',
                #     '-v',
                #     'error',
                #     '-show_entries',
                #     'format=duration',
                #     '-of',
                #     'default=noprint_wrappers=1:nokey=1',
                #     video_url
                # ]
                #
                # if (duration == None):
                #     output = check_output(command, stderr=STDOUT).decode()
                #     duration = round(float(output) / 60, 2)
                #     duration = str(duration).replace('.', ':')
                #     duration = '0:' + duration
                # else:
                #     duration = round(float(duration) / 60, 2)
                #     duration = str(duration).replace('.', ':')
                #     duration = '0:' + duration

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
            except Exception as err:
                print("TIME ERROR",err)

            modified_video_keywords = [x.strip() for x in video_keywords.split()]

            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5ede1404c2939c7f01a079d4",   #Not yet changed
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
        except Exception as err:
            print("URL MISSING",err)