# from scrapy.loader import ItemLoader
# from scrapy.selector import Selector
# from urllib.parse import urlparse
# import scrapy, re, json,sys, json, html, re
# from slugify import slugify
# from ..database.Queries import Queries
# from time import strftime
# from time import gmtime
# from moviepy.video.io.VideoFileClip import VideoFileClip
#
# class News18(scrapy.Spider):
#     name="page_news18"
#     start_urls=[
#         'https://www.news18.com/videos/',
#         ]
#     user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
#     def parse(self, response):
#         hxs = Selector(response)
#         links = hxs.xpath("//div[@class = 'vdo-innerbox']/ul/li/a/@href").extract()
#         print ("NEWS18 Started")
#         for link in links:
#             url = link
#             yield scrapy.Request(url, callback=self.parse_subpage)
#     def parse_subpage(self, response):
#         try:
#             global video_url, url, duration, video_keywords, title, description, image, modified_video_keywords, modified_time
#             try:
#                 video_url=response.xpath('//script[contains(., "hola_player")]/text()').re('src: "(.+)"')[0]
#                 clip = VideoFileClip(video_url)
#                 dur = clip.duration
#                 duration = strftime("%H:%M:%S", gmtime(dur))
#                 title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
#                 description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
#                 image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
#                 video_keywords = response.xpath("//meta[@name = 'news_keywords']/@content").extract_first()
#             except:
#                 print("ERROR IN NEWS18")
#             try:
#                 modified_video_keywords = [x.strip() for x in video_keywords.split()]
#             except:
#                 print("SPLIT ERROR")
#             keywords = Queries.insert_keywords(self, modified_video_keywords)
#             insertObject = {
#                 "video_title" : title,
#                 "video_slug" : slugify(title),
#                 "video_link" : video_url,
#                 "video_description" : description,
#                 "broadcaster" : "5d5b8bda11857574e9d440d5",   #Not yet changed
#                 "videoformat" : "5ce4f7ffa5c038104cb76649",   #Not yet changed
#                 "video_image" : image,
#                 "videokeywords" : keywords,
#                 "page_url" : response.url,
#                 "duration" : duration
#             }
#             # Queries.insert_videos(self, insertObject)
#             result = Queries.insert_api(self, insertObject)
#             if result.status_code == 200:
#                 print("INSERTED")
#             else:
#                 print(result.status_code)
#                 print(result)
#         except:
#             print("URL MISSSING")