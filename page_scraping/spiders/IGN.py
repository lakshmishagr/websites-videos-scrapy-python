from subprocess import  check_output, CalledProcessError, STDOUT

from scrapy.loader import ItemLoader
from  scrapy.selector import Selector
from urllib.parse import urlparse
import scrapy, re, json,sys, json, html, re
from slugify import slugify
from ..database.Queries import Queries

class IGN(scrapy.Spider):
    name="page_ign"
    start_urls=[
        'https://in.ign.com/video'
        ]
    def parse(self, response):
        hxs = Selector(response)
        links1 = hxs.xpath("//div[@class = 't']/a/@href").extract()
        links2=hxs.xpath("//a[@class = 'slotter-item']/@href").extract()
        print("IGN Started")
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        category = '{uri.path}'.format(uri=parsed_uri)
        category = category.split('/')
        if ("video" in category):
            category = "games"
        links= links1 + links2
        print(len(links))
        # links = links[0:3]
        for link in links:
            url = link
            print("aaa--",link)
            request = scrapy.Request(url, callback=self.parse_subpage)
            request.meta['category'] = category
            yield request
    def parse_subpage(self, response):
        global url, video_url, duration, modified_time, video_keywords, modified_video_keywords, title, description, image, category
        try:
            try:
                # video_url=response.xpath("//div[@class='vplayer']/iframe/@src").extract_first()
                # print(video_url)
                # duration=response.xpath("//span[@class='duration']/span/text()").extract_first()
                # title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
                # description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
                # image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
                category = response.meta['category']
                # video_keywords = title
                # print(duration)
                im = response.xpath("//section[@id='js']").extract_first()
                im = im.split('</script>')
                im = [s for s in im if "contentUrl" in s]
                im = im[0].replace('"','').replace('\n','').replace('<','').replace('>','').replace('{','').replace('}','').replace('@','')
                im = im.split(',')
                video_url = [s for s in im if "contentUrl" in s]
                video_url = video_url[0].replace('contentUrl:','').replace(' ','')
                duration = [s for s in im if "duration" in s]
                duration = duration[0].replace('duration:','').replace('PT','00:').replace('M',':').replace('S','').replace(' ','')
                image = [s for s in im if "thumbnailUrl" in s]
                image = image[0].replace('thumbnailUrl:','').replace(' ','')
                title = [s for s in im if "name" in s]
                title = title[0].replace('name:','').replace(' ','')
                description = [s for s in im if "description" in s]
                description = description[0].replace('description:','').replace(' ','')

            except:
                print("Exception hit")
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
                print("Error",err)

            try:
                modified_video_keywords = [x.strip() for x in title.split()]
            except:
                print("modified keywords error")
            keywords = Queries.insert_keywords(self, modified_video_keywords)
            if video_url.startswith('slike-v.akamaized.net'):
                video_url = "https://"+ video_url
            if video_url.startswith('//vslike.akamaized.net'):
                video_url = "https:"+ video_url
            if video_url.startswith('//slike-v.akamaized.net'):
                video_url = "https:"+ video_url

            insertObject = {
                "video_title": title,
                "video_slug": slugify(title),
                "video_link": video_url,
                "video_description": description,
                "broadcaster" : "5d1ef40f43eefdb023bf9d84",   #Not yet changed
                "videoformat" : "5ce4f7eda5c038104cb76648",   #Not yet changed
                "video_image": image,
                "videokeywords": keywords,
                "page_url": response.url,
                "duration": modified_time,
                "category": category,
                "language": "english",
                "keywords": ' | '.join(map(str, modified_video_keywords))
            }

            if ((len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8)  and video_url.startswith('http') and (video_url.endswith('.mp4') or video_url.endswith('.m3u8'))):
                print("aaa------------------aaaa")
                print(title)
                print(video_url)
                print(modified_time)
                print(image)
                print(category)
                print("english")
                # # print(insertObject)
                # print(modified_video_keywords)
                print("bbb------------------bbb")
                result = Queries.insert_api(self, insertObject)
                if result.status_code == 200:
                    print("INSERTED")
                else:
                    print(result.status_code)
                    print(result.json())

        except Exception as err:
            print("misskyra error", err)




