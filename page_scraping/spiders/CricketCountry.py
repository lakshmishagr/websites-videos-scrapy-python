# from scrapy.loader import ItemLoader
# from  scrapy.selector import Selector
# from urllib.parse import urlparse
# import scrapy, re, json,sys, json, html, re
# from slugify import slugify
# from ..database.Queries import Queries
# from subprocess import  check_output, CalledProcessError, STDOUT
#
# class CricketCountry(scrapy.Spider):
#     name="page_cricketcountry"
#     start_urls=[
#         'https://www.cricketcountry.com/videos/'
#         ]
#     def parse(self, response):
#         hxs = Selector(response)
#         links = hxs.xpath("//section[@class = 'container']/aside[@class = 'container-left']/ul/li/figure/a/@href").extract()
#         print("CRICKETCOUNTRY Started")
#         for link in links:
#             url = link
#             yield scrapy.Request(url, callback=self.parse_subpage)
#     def parse_subpage(self, response):
#         try:
#             video_url=response.xpath('//script[contains(., "var video_file")]/text()').re('var video_file += "(.+)"')[0] #others
#             url = response.xpath("//meta[@property = 'og:url']/@content").extract_first()
#             title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
#             print("\n",title)
#             description = response.xpath("//meta[@name = 'description']/@content").extract_first()
#             #if (description =="" or "None"):
#                 #print("error des")
#                 #description = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
#             #else:
#                 #print("no desction----------------------")
#             image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
#             video_keywords = response.xpath("//meta[@name = 'keywords']/@content").extract_first()
#             yield {
#                 'titlt':response.xpath("//meta[@property = 'og:title']/@content").extract_first()
#             }
#             command = [
#                 'ffprobe',
#                 '-v',
#                 'error',
#                 '-show_entries',
#                 'format=duration',
#                 '-of',
#                 'default=noprint_wrappers=1:nokey=1',
#                 video_url
#             ]
#
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
#                 time3 = time[2] if int(time[2]) > 9 else '0'+time[2]
#                 modified_time = str(time1+":"+time2+":"+time3)
#                 print(modified_time)
#             except:
#                 print("TIME ERROR")
#             #print(video_url, title, description, image, video_keywords, duration)
#             try:
#                 modified_video_keywords = [x.strip() for x in video_keywords.split()]
#                 print(modified_video_keywords)
#             except:
#                 print("SPLIT ERROR")
#             # keywords = Queries.insert_keywords(self, modified_video_keywords)
#             insertObject = {
#                 "video_title" : title,
#                 # "video_slug" : slugify(title),
#                 "video_link" : video_url,
#                 "video_description" : description,
#                 "broadcaster" : "5d247635d106ef35f2d72712",
#                 "videoformat" : "5ce4f7eda5c038104cb76648",
#                 "video_image" : image,
#                 # "videokeywords" : keywords,
#                 "page_url": response.url,
#                 "duration" : modified_time
#             }
#             print(insertObject)
#
#
#         #     result = Queries.insert_api(self, insertObject)
#         #     if result.status_code == 200:
#         #         print("INSERTED")
#         #     else:
#         #         print(result.status_code)
#         #         print(result)
#         except:
#             print("VIDEO URL NOT PROPER")
