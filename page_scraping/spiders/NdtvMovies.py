from urllib import response

from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries

class NdtvMovies(scrapy.Spider):
    name="page_ndtvmovies"
    start_urls=[
        'https://movies.ndtv.com/videos/latest-video',
        'https://movies.ndtv.com/videos?pfrom=home-videos',
        'https://movies.ndtv.com/tamil/videos',
        ]
    def parse(self, response):
        langcheck = "en"
        print("started")
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        data = '{uri.path}'.format(uri=parsed_uri)
        if("tamil" in data):
            langcheck = "tamil"
        category = "entertainment|Movies"
        lang = 'english'
        if('/video/latest-video' == data) :
            links = hxs.xpath("//div[@class = 'ndmv-celeb-blk']/div/a/@href").extract()
        else :
            links = hxs.xpath("//div[@class ='ndmv-common-img-wrapper']/a/@href").extract()

        print(len(links))
        # links = links[0:3]
        for link in links:
            url = link
            # print('aaa-',url)
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            request.meta['langcheck'] = langcheck
            yield request
    def parse_subpage(self, response):
        # print("subpage")
        try:
            global video_url, url, duration, video_keywords, title, description, image, modified_time, category, lang, modified_video_keywords
            url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
            langcheck = response.meta['langcheck']
            try:
                if(langcheck == "tamil") :
                    url = response.xpath('//script[contains(.,"__html5playerdata")]').re('"media":"(.+)"')[0]
                else:
                    url=response.xpath('//script[contains(., "__html5playerdata")]/text()').re('"media_mp4":"(.+)"')[0]

                video = url.split('","')[0]
                video_url = video.replace('\\', '')
                # print(video_url)
                url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
                # print(url)
                title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                # print(title)
                description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                # print(description)
                image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                # print(image)
                video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
                # print(video_keywords)
                duration = response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration": +"(.+)"')[0]
                # print(duration)
                duration = duration.replace('PT','0:').replace('M', ':').replace('S','')
                # print(duration)
                # yield {
                #     'food': response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                # }
                category = response.meta['category']
                lang = response.meta['lang']
                if(langcheck == 'tamil'):
                    lang = "tamil"
                else:
                    try:
                        title.encode(encoding='utf-8').decode('ascii')
                    except UnicodeDecodeError:
                        lang = "hindi"
                    else:
                        lang = "english"

            except:
                print("EXCEPTION HIT")
            try:
                time = duration.split(':')
                time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
                time2 = time[1] if int(time[1]) > 9 else '0'+time[1]
                time3 = time[2] if int(time[2]) > 9 else '0'+time[2]
                modified_time = str(time1+":"+time2+":"+time3)
            except:
                print("TIME ERROR")
            # print(video_url, duration, title, description, image, video_keywords)
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
                "broadcaster" : "5d3e9dde3b6d5e43e2ef58ec",   #Not yet changed
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
                # # # print(insertObject)
                # print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result)

        except:
            print("URL MISSING")