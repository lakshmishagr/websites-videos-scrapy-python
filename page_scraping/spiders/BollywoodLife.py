# from scrapy.loader import ItemLoader
# from scrapy.selector import Selector
# from urllib.parse import urlparse
# import scrapy, re, json, sys, json, html, re
# from slugify import slugify
# from ..database.Queries import Queries
#
# from subprocess import  check_output, CalledProcessError, STDOUT
#
# class BollywoodLife(scrapy.Spider):
#     name = "page_bollywoodlife"
#     start_urls = [
#         'https://www.bollywoodlife.com/videos-gallery/'
#     ]
#     user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
#     def parse(self, response):
#         hxs = Selector(response)
#         links = hxs.xpath("//div[@class = 'story_img_Blk']/a/@href").extract()
#         print(links)
#         print("BOLLYWOODLIFE started")
#         for link in links:
#             url = link
#             yield scrapy.Request(url, callback=self.parse_subpage)
#
#     def parse_subpage(self, response):
#         try:
#             #url=response.xpath("//section[@class = 'article_container']/aside/div[@class = 'art_content']/p/iframe/@src").extract_first() #youtube
#
#             try:
#                 video_url=response.xpath('//script[contains(., "var video_file")]/text()').re('var video_file += "(.+)"')[0]
#
#                 if(video_url == None or video_url == "" ):
#                     print("video url None")
#                     raise Exception("its not video url")
#                 else:
#                     pass
#                 url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
#                 title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
#                 yield {
#                     'title':response.xpath("//meta[@property = 'og:title']/@content").extract_first()
#                 }
#                 description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
#                 image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
#                 video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
#                 command = [
#                     'ffprobe',
#                     '-v',
#                     'error',
#                     '-show_entries',
#                     'format=duration',
#                     '-of',
#                     'default=noprint_wrappers=1:nokey=1',
#                     video_url
#                 ]
#
#             except:
#                 print("EXCEPTION HIT")
#             try:
#                 output = check_output( command, stderr=STDOUT ).decode()
#                 duration = round(float(output)/60, 2)
#                 duration = str(duration).replace('.',':')
#                 duration = '0:'+duration
#             except CalledProcessError as e:
#                 output = e.output.decode()
#
#             try:
#                 time = duration.split(':')
#                 time1 = time[0] if int(time[0]) > 9 else '0'+time[0]
#                 time2 = time[1] if int(time[1]) > 9 else '0'+time[1]
#                 time3 = time[2] #if int(time[2]) > 9 else '0'+time[2]
#                 modified_time = str(time1+":"+time2+":"+time3)
#             except:
#                 print("ERROR")
#             try:
#                 modified_video_keywords = [x.strip() for x in video_keywords.split()]
#             except:
#                 print("SPLIT ERROR")
#             # keywords = Queries.insert_keywords(self, modified_video_keywords)
#             insertObject = {
#                 "video_title": title,
#                 # "video_slug": slugify(title),
#                 "video_link": video_url,
#                 "video_description": description,
#                 "broadcaster": "5d247283d106ef35f2d72711",  #Not yet changed
#                 "videoformat": "5ce4f7eda5c038104cb76648",  #Not yet changed
#                 "video_image": image,
#                 # "videokeywords": keywords,
#                 "page_url": response.url,
#                 "duration" : modified_time
#                 }
#
#
#             print("\nobj",insertObject)
#             #         # if (len(video_url) > 0 and len(image) > 0 and len(modified_time) == 8):
#             #         #
#             #         #     result = Queries.insert_api(self, insertObject)
#             #         #     if result.status_code == 200:
#             #         #         print("INSERTED")
#             #         #     else:
#             #         #         print(result.status_code)
#             #         #         print(result.json())
#         except:
#             print("Url missing")
#
