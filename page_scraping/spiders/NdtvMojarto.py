# from scrapy.loader import ItemLoader
# from  scrapy.selector import Selector
# from urllib.parse import urlparse
# import scrapy, re, json,sys, json, html, re
# from slugify import slugify
# from ..database.Queries import Queries
#
# class NdtvMojarto(scrapy.Spider):
#     name="page_ndtvmojarto"
#     start_urls=[
#         'https://www.mojarto.com/the-world-of-mojarto'
#         ]
#     def parse(self, response):
#         hxs = Selector(response)
#         links = hxs.xpath("//div[@class = 'story_listing']/ul[@class = 'blog-list']/li/div/span/a/@href").extract()
#         print("MOJARTO Started")
#         for link in links:
#             parsed_uri = urlparse(response.url)
#             domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
#             url = domain + link
#             print(url)
#             yield scrapy.Request(url, callback=self.parse_subpage)
#     def parse_subpage(self, response):
#         print("subvalues")
#         try:
#             global video_url, url, duration, video_keywords, title, description, image, modified_video_keywords, modified_time
#             try:
#                 video_url=response.xpath("//div[@class = 'main_story']/iframe/@src").extract_first()
#                 if(video_url == None):
#                     video_url = response.xpath("//a[@class = 'st-e-mail']/@data-url").extract_first()
#                 # print('2',video_url)
#                 title = response.xpath("//title/text()").extract_first()
#                 # print('3',title)
#                 description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
#                 # print('4',description)
#                 image = response.xpath("//div[@class = 'ytp-cued-thumbnail-overlay']/div[@class = 'ytp-cued-thumbnail-overlay-image']/@styles/text()").re('background-image.*/([^/]+)') #image urls are missing because it is youtube videos
#                 # print('5',image)
#                 video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
#                 # print('6',video_keywords)
#                 if (video_keywords == ""):
#                     list = title.split()
#                     video_keywords = ', '.join(map(str, list))
#                     # print('7',video_keywords)
#                 else:
#                     print("key words found nothing to split")
#
#             except:
#                 print("EXCEPTION HIT")
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
#                 "broadcaster" : "5d3e9d793b6d5e43e2ef58eb",   #Not yet changed
#                 "videoformat" : "5ce4f7eda5c038104cb76648",   #Not yet changed
#                 "video_image" : image,
#                 "videokeywords" : keywords,
#                 "url": response.url,
#                 "duration" : modified_time,
#                 "category" :"mojarto",
#                 "language" :"english",
#                 "keywords": ' | '.join(map(str, modified_video_keywords))
#             }
#             if ((len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8)
#                     and (video_url.endswith('.m3u8') or video_url.endswith('.mp4'))):
#                 # print("aaa------------------aaaa")
#                 # print(title)
#                 # print(video_url)
#                 # print(modified_time)
#                 # print(image)
#                 # # print(category)
#                 # # print(lang)
#                 # # # print(insertObject)
#                 # print("bbb------------------bbb")
#                 result = Queries.insert_api(self, insertObject)
#                 if result.status_code == 200:
#                     print("INSERTED")
#                 else:
#                     print(result.status_code)
#                     print(result)
#         except:
#             print("URL MISSING")