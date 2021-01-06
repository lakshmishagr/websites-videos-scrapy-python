from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html
from slugify import slugify
from ..database.Queries import Queries

class TimesNownewsSub(scrapy.Spider):
    name='page_timesnownewsSub'
    start_urls=[
        # 'https://www.timesnownews.com/videos/times-now',
        # 'https://www.timesnownews.com/videos/et-now',
        # 'https://www.timesnownews.com/videos/health',
        # 'https://www.timesnownews.com/videos/lifestyle',
        # 'https://www.timesnownews.com/videos/mirror-now',
        # 'https://www.timesnownews.com/videos/foodie',
        'https://www.timesnownews.com/videos/times-drive',
        'https://www.timesnownews.com/videos/times-now',
        'https://www.timesnownews.com/videos/news-plus',
        'https://www.timesnownews.com/videos/zoom',
        'https://www.timesnownews.com/videos/web-series',
        'https://www.timesnownews.com/videos'
    ]
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"

    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        lang = "english"
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        print(category)
        if ("times-now" in category):
            category = "news"
        if ("et-now" in category):
            category = "economics"
        if ("health" in category):
            category = "health"
        if ("lifestyle" in category):
            category = "lifestyle"
        if ("mirror-now" in category):
            category = "news"
        if ("foodie" in category):
            category = "food"
        if ("times-drive" in category):
            category = "automobiles"
        if ("times-now" in category):
            category = "news"
        if ("news-plus" in category):
            category = "news"
        if("web-series" in category) :
            category ="entertainment"
        if ("zoom" in category):
            category = "celebrity"

        if("videos" in category and len(category) ==2 ) :
            category = "news"
            links = hxs.xpath("//a[@class='video']/@href").extract()
        else:
            links1 = hxs.xpath("//a[@class='banner-slot']/@href").extract()
            links2 = hxs.xpath("//a[@class='video']/@href").extract()
            links = links1 + links2

        links = links[0:50]
        print(len(links))
        for link in links:
            url = link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            yield request

    def parse_subpage(self, response):
        try:
            global video_url, url, duration, video_keywords, title, description, image, modified_video_keywords, modified_time, news_keywords, category, lang
            try:
                video_url = response.xpath("//div[@class='video-pod']/div/@data-src").extract_first()
                duration = response.xpath("//input[@id='ad_duration']/@value").extract_first()
                duration = duration.replace('T','').replace('MIN', ':').replace('SEC','').replace(' ', '')
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                news_keywords = response.xpath("//meta[@name ='keywords']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                duration = '0:'+duration
                category = response.meta['category']
                lang = response.meta['lang']
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
                print("TIME ERROR")
            try:
                modified_video_keywords = [x.strip() for x in news_keywords.split()]
            except:
                print("SPLIT ERROR")
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5d1ef58d43eefdb023bf9d85",
                "videoformat" : "5ce4f7ffa5c038104cb76649",
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
        except:
            print("URL MISSING")