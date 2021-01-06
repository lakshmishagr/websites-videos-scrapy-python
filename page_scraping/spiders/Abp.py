# # from demo.items import JokeItem
# from scrapy.loader import ItemLoader
# from scrapy.selector import Selector
# import urllib.request as Request
# import scrapy
# import xml.etree.ElementTree as ET
# from xml.dom import minidom
# import json
# from slugify import slugify
# from ..database.Queries import Queries
#
#
#
# def remove_whitespace(value):
#     return value.strip()
#
# class AbpLive(scrapy.Spider):
#     name = 'page_scraping' ##Spider Identifier
#
#     ##Code starts from here
#     def start_requests(self):
#         user_agent ='Mozilla/5.0 (Android; Tablet) AppleWebKit/537.36 (KHTML, like Gecko; Android; Tablet; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/72.0.3626.121 Safari/537.36'
#         url = "https://www.abplive.in/videos/feed"
#         request = Request.Request(url)
#         request.add_header('User-Agent', user_agent)
#         request.get_header('Accept')
#         xml = ET.parse(Request.urlopen(request))
#         root = xml.getroot()
#         print("ABP Started")
#         for ele in root.findall("channel/item/link"):
#             yield scrapy.Request(remove_whitespace(ele.text), self.parse)
#
#     ##Parse the page
#     def parse(self, response):
#         global video_url, duration, title, news_keywords, description, image
#         hxs = Selector(response)
#         try:
#             dur=response.xpath('//script[@type = "application/ld+json"]/text()').re('"duration": "(.+)"')[0]
#             duration = dur.replace('PT','').replace('H', ':').replace('M', ':').replace('S','').replace('s','').replace(' ', '')
#             video_url = hxs.xpath("//meta[@property = 'og:video']/@content").extract_first()
#             title = hxs.xpath("//meta[@property = 'og:title']/@content").extract_first()
#             news_keywords = hxs.xpath("//meta[@name ='news_keywords']/@content").extract_first()
#             description = hxs.xpath("//meta[@property = 'og:description']/@content").extract_first()
#             image = hxs.xpath("//meta[@property = 'og:image']/@content").extract_first()
#         except:
#             print("Exception Hit")
#             pass
#         try:
#             modified_keywords = [x.strip() for x in news_keywords.split(',')]
#         except:
#             print("SPLIT ERROR")
#         try:
#             time = duration.split(':')
#             time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
#             time2 = time[1] if int(time[1]) > 9 else '0'+time[1]
#             time3 = time[2] if int(time[2]) > 9 else '0'+time[2]
#             modified_time = str(time1+":"+time2+":"+time3)
#         except:
#             print("TIME ERROR")
#         # keywords = Queries.insert_keywords(self, modified_keywords)
#         insertObject = {
#             "video_title" : title,
#             # "video_slug" : slugify(title),
#             "video_link" : video_url,
#             "video_description" : description,
#             "broadcaster" : "5cc14c8de7802c116165f920",
#             "videoformat" : "5ce4f7ffa5c038104cb76649",
#             "video_image" : image,
#             # "videokeywords" : keywords,
#             "page_url": response.url,
#             "duration" : modified_time
#         }
#         print(insertObject)
#         # result = Queries.insert_api(self, insertObject)
#         # if result.status_code == 200:
#         #     print("INSERTED")
#         # else:
#         #     print(result.status_code)
#         #     print(result.json())
#         #
#
#         # yield scrapy.Request(url=content, callback=self.parse)
