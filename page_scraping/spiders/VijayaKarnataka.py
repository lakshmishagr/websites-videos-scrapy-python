from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json, sys, json, html
from slugify import slugify
from ..database.Queries import Queries


class VijayaKarnataka(scrapy.Spider):
    name = "page_vijayakarnataka"
    start_urls = [
        # 'https://vijaykarnataka.com/video/videolist/49909262.cms',
        'https://vijaykarnataka.com/video/entertainment/videolist/50075616.cms',
        'https://vijaykarnataka.com/elections/assembly-elections/karnataka-elections/video/videolist/63431237.cms',
        'https://vijaykarnataka.com/video/business/videolist/50075709.cms',
        'https://vijaykarnataka.com/video/sports/videolist/50075699.cms',
        'https://vijaykarnataka.com/video/beauty-pageants/videolist/50094968.cms',
        'https://vijaykarnataka.com/video/news/videolist/50075603.cms'
        'https://vijaykarnataka.com/video/karnataka-news/videolist/60309788.cms',
        'https://vijaykarnataka.com/video/kannada-cinema/videolist/60309722.cms',
        'https://vijaykarnataka.com/video/health/videolist/60309735.cms',
        'https://vijaykarnataka.com/video/latest/videolist/61139304.cms'
    ]

    def parse(self, response):
        hxs = Selector(response)
        links = hxs.xpath("//div[@class = 'sliderkit-nav-clip vdlist']/ul/li/a/@href").extract()
        # links = hxs.xpath("//div[@class = 'contentarea']/div[@class = 'sliderkit']/div[@class = 'sliderkit-nav']/div[@class = 'sliderkit-wrap']/div[@class = 'sliderkit-nav-clip']/ul/li/a/@href").extract()
        print("VIJAYAKARNATAKA Started")
        # print(len(links))
        links = links[0:5]
        # print(len(links))
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        if("entertainment" in category):
            category = "entertainment"
        if ("elections" in category):
            category = "politics"
        if ("business" in category):
            category = "business"
        if ("sports" in category):
            category = "sports"
        if ("beauty-pageants" in category):
            category = "beauty"
        if ("news" in category):
            category = "news"
        if ("kannada-cinema" in category):
            category = "cinema"
        if ("health" in category):
            category = "health"
        if ("latest" in category):
            category = "news"
        print(category)
        for link in links:
            print("aaaa--",link)
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain + link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request

    def parse_subpage(self, response):
        try:
            global video_url, url, duration, video_keywords, title, description, image, modified_time, category, modified_video_keywords, keywords
            try:
                video_url = response.xpath("//script[@type = 'application/ld+json']/text()").re('(.+) "contentUrl": "(.+)"')[1]
                duration = response.xpath("//script[@type = 'application/ld+json']/text()").re('(.+) "duration": "(.+)"')[1]
                duration = duration.replace('T', '').replace('M', ':').replace('S', '').replace('s', '').replace(' ','')
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                video_keywords = response.xpath("//meta[@name = 'Keywords']/@content").extract_first()
                duration = '0:' + duration
                category = response.meta['category']
            except Exception as err:
                print("vijaya 1  ",err)
            try:
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0' + time[0]
                time2 = time[1] if int(time[1]) > 9 else '0' + time[1]
                time3 = time[2]  # if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1 + ":" + time2 + ":" + time3)
            except Exception as err:
                print("vijaya 2  ", err)
            try:
                modified_video_keywords = [x.strip() for x in video_keywords.split()]
                keywords = Queries.insert_keywords(self, modified_video_keywords)
            except:
                print("vijaya SPLIT ERROR")

            insertObject = {
                "video_title": title,
                "video_slug": slugify(title),
                "video_link": video_url,
                "video_description": description,
                "broadcaster": "5d3ea23a3b6d5e43e2ef5999",
                "videoformat": "5ce4f7eda5c038104cb76648",
                "video_image": image,
                "videokeywords": keywords,
                "page_url": response.url,
                "duration": modified_time,
                "category": category,
                "language": "kannada",
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }
            if ((len(video_url)>0 and len(image)>0 and len(modified_time)==8) and
                    (video_url.endswith('.mp4') or video_url.endswith('.m3u8'))):
                # print("aaa------------------aaaa")
                # print(title)
                # print(video_url)
                # print(modified_time)
                # print(image)
                # print(category)
                # print("kannada")
                # print("")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result)
        except Exception as err:
            print("vijaya 3  ", err)