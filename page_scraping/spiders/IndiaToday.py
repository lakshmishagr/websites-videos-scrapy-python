from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries
from subprocess import  check_output, CalledProcessError, STDOUT 

class IndiaToday(scrapy.Spider):
    name="page_indiatoday"
    start_urls=[

        'https://www.indiatoday.in/videos/sports/',
        'https://www.indiatoday.in/videos/movies/',
        'https://www.indiatoday.in/videos/news',
        'https://www.indiatoday.in/videos/india',
        'https://www.indiatoday.in/videos/entertainment',
        'https://www.indiatoday.in/videos/technology',
        'https://www.indiatoday.in/videos',
        ]
    def parse(self, response):
        hxs = Selector(response)
        print("IndiaToday Started")
        links = hxs.xpath("//div[@class='tile']/figure/a/@href").extract()
        links = hxs.xpath("//div[@class='detail']/h2/a/@href").extract()
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        if ("sports" in category):
            category = "sports"
        if ("movies" in category):
            category = "entertainment"
        if ("news" in category):
            category = "news"
        if ("india" in category):
            category = "news"
        if ("entertainment" in category):
            category = "entertainment"
        if ("technology" in category):
            category = "technology"
        if ("videos" in category and len(category) == 2):
            category = "news"
        for link in links:
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain + link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request

    def parse_subpage(self, response):
        try:
            global video_url, url, title, image, description, video_keywords, modified_time, modified_video_keywords, duration, category
            try:
                url = (response.xpath('//script[@type="application/ld+json"]/text()').extract_first())
                data = json.loads(url, strict=False)
                try:
                    video_url = (data["contentUrl"])
                except:
                    print("VideoUrl missed")
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                if (description == ""):
                    description=title
                else:
                    pass
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords = response.xpath("//meta[@name = 'news_keywords']/@content").extract_first()
                if (video_keywords == ""):
                    list = title.split()
                    video_keywords=', '.join(map(str,list))
                else:
                    pass
                category = response.meta['category']

            except:
                print("Exception Hit")
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
            try:
                output = check_output( command, stderr=STDOUT ).decode()
                duration = round(float(output)/60, 2)
                duration = str(duration).replace('.', ':')
                duration = '0:'+duration
            except CalledProcessError as e:
                output = e.output.decode()
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

            modified_video_keywords = [x.strip() for x in video_keywords.split()]
            keywords = Queries.insert_keywords(self, modified_video_keywords)

            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d0cb8a757a7812e3c74c76a",
                "videoformat" : "5ce4f7eda5c038104cb76648",
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration" : modified_time,
                "category": category,
                "language": "english",
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
            print("indiatoday error", err)