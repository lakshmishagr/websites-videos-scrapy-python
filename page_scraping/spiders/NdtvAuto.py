from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html
from slugify import slugify
from ..database.Queries import Queries

class NdtvAuto(scrapy.Spider):
    name="page_ndtvauto"
    start_urls=[
        'https://auto.ndtv.com/videos/all'
        ]
    def parse(self, response):
        hxs = Selector(response)
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = "automobiles"
        lang = 'english'
        links1 = hxs.xpath("//div[@class = 'grid_15']/a/@href").extract()
        links2 = hxs.xpath("//li[@class ='video__item']/a/@href").extract()
        links = links1 + links2
        print("NDTV AUTO Started")
        print(len(links))
        for link in links:
            # print("aaa--",link)
            parsed_uri = urlparse(response.url)
            domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
            url = domain + link
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            request.meta['lang'] = lang
            yield request

    def parse_subpage(self, response):
        print("subvalues")
        try:
            global data, video_url, title, description, image, video_keywords, modified_time, modified_video_keywords
            category = response.meta['category']
            lang = response.meta['lang']
            data = response.xpath("//div[@id='deferred_javascript']").extract_first()
            data = data.replace('<','').replace('>','').replace('<!--', '').replace('-->', '').replace('\n','').replace("'",'').replace(' ','')
            data= data.split(',')
            res = [i for i in data if 'media_mp4' in i]
            video_url = res[0].replace('media_mp4:','')
            # print(video_url)
            # url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
            title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
            # print(title)
            description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
            # print(description)
            image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
            # print(image)
            video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
            # print(video_keywords)
            duration = response.xpath("//meta[@itemprop ='duration']/@content").extract_first()
            duration = duration.replace('PT','0:').replace('M',':').replace('S','')
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
                modified_video_keywords = [x.strip() for x in video_keywords.split()]
                # print(modified_video_keywords)
            except:
                print("SPLIT ERROR")
            keywords = Queries.insert_keywords(self, modified_video_keywords)

            insertObject = {
                "video_title" : title,
                "video_slug" : slugify(title),
                "video_link" : video_url,
                "video_description" : description,
                "broadcaster" : "5eda3ddd3a51c667efdcdf7d",   #Not yet changed
                "videoformat" : "5ce4f7eda5c038104cb76648",   #Not yet changed
                "video_image" : image,
                "videokeywords" : keywords,
                "page_url": response.url,
                "duration": modified_time,
                "category": category,
                "language": lang,
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }
            if ((len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8)
                    and (video_url.endswith('.m3u8') or video_url.endswith('.mp4'))):
                # print("aaa------------------aaaa")
                # print(title)
                print(video_url)
                # print(modified_time)
                # print(image)
                # print(category)
                # print(lang)
                # print(insertObject)
                # print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result)
        except:
            print("URL MISSING")