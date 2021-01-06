from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries
from subprocess import  check_output, CalledProcessError, STDOUT

class BollywoodHungamaEng(scrapy.Spider):
    name="page_bollywoodhungamaeng"
    start_urls=[

        'https://www.bollywoodhungama.com/top-videos/',
        'https://www.bollywoodhungama.com/videos/making-of-the-music/',
        'https://www.bollywoodhungama.com/videos/movie-promos/',
        'https://www.bollywoodhungama.com/videos/celeb-interviews/',
        'https://www.bollywoodhungama.com/videos/making-of-movies/',
        'https://www.bollywoodhungama.com/videos/parties-events/',
        'https://www.bollywoodhungama.com/videos/first-day-first-show/',
        ]
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
    def parse(self, response):
        hxs = Selector(response)
        link1 = hxs.xpath("//article[@class = 'bh-cm-box bh-box-article hentry']/figure/a/@href").extract()
        link2 =hxs.xpath("//div[@class = 'video-list-box clearfix']/figure/a/@href").extract()
        links=link1+link2
        category = "entertainment"
        print("Bollywood ENG Started")
        print(len(links))
        for link in links:
            url = link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request


    def parse_subpage(self, response):
        print("subvalues")
        try:
            global video_url, duration, video_keywords, title, description, image, modified_video_keywords, modified_time, category
            try:
                video_url=response.xpath("//div/meta[@itemprop='contentURL']/@content").extract_first()
                video_keywords=response.xpath("//meta[@name = 'keywords']/@content").extract_first()
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                category = response.meta['category']
                duration = None
                print("\n",video_url)
            except:
                print("EXCEPTION HIT")
            command = [
                'ffprobe',
                '-v',
                'error',
                '-show_entries',
                'format=duration',
                '-of',
                'quiet',
                'csv=p=0',
                'default=noprint_wrappers=1:nokey=1',
                video_url
            ]
            try:
                if (duration == None):
                    output = check_output(command, stderr=STDOUT).decode()
                    print("\noutput", output)
                    duration = round(float(output) / 60, 2)
                    duration = str(duration).replace('.', ':')
                    duration = '0:' + duration
                    print("\ndur", duration)
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
                "broadcaster" : "5edf39ec820f925d307ae315",   #Not yet changed
                "videoformat" : "5ce4f7ffa5c038104cb76649",   #Not yet changed
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration" : modified_time,
                "category": category,
                "language": "english",
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }
            if ((len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8) and
                    (video_url.endswith('.mp4') or video_url.endswith('.m3u8') or video_url.endswith('.m4v'))):
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
            print("BollywoodEng error", err)
