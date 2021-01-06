# from scrapy.loader import ItemLoader
# from scrapy.selector import Selector
# from urllib.parse import urlparse
# import scrapy, re, json,sys, json, html, re
# from slugify import slugify
# from ..database.Queries import Queries
# from moviepy.video.io.VideoFileClip import VideoFileClip
# from time import strftime
# from time import gmtime
#
# class KannadaNews18(scrapy.Spider):
#     name="page_kannadanews"
#     start_urls=[
#         'https://kannada.news18.com/videos/state/disqualified-mla-muniratna-angry-against-dk-shivakumar-sh-218091.html'
#         'https://kannada.news18.com/videos/sports/',
#         'https://kannada.news18.com/videos/astro/',
#         'https://kannada.news18.com/videos/trend/',
#         'https://kannada.news18.com/videos/national-international/',
#         'https://kannada.news18.com/videos/entertainment/',
#         'https://kannada.news18.com/videos/tech/',
#         'https://kannada.news18.com/videos/state/',
#         'https://kannada.news18.com/videos/lifestyle/'
#         ]
#     user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
#     def parse(self, response):
#         hxs = Selector(response)
#         links = hxs.xpath("//div[@class = 'data-list-cat']/figure/a/@href").extract()
#         print("KANNADANEWS Started")
#         for link in links:
#             parsed_uri = urlparse(response.url)
#             domain = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
#             url = domain+link
#             # print (url)
#             yield scrapy.Request(url, callback=self.parse_subpage)
#
#     def parse_subpage(self, response):
#         try:
#             global video_url, url, duration, title, description, image, video_keywords, modified_video_keywords
#             url = response.xpath('//script[@type = "application/ld+json"]/text()').extract()[1]
#             video_url = json.loads(url, strict=False)
#             video_url =  (video_url["embedUrl"])
#             try:
#                 clip = VideoFileClip(video_url)
#                 dur = clip.duration
#                 duration = strftime("%H:%M:%S", gmtime(dur))
#             except:
#                 print("TIME ERROR")
#             # print(duration)
#             title = response.xpath("//meta[@property = 'og:title']/@content").extract_first()
#             description = response.xpath("//meta[@property = 'og:description']/@content").extract_first()
#             image = response.xpath("//meta[@property = 'og:image']/@content").extract_first()
#             video_keywords = response.xpath("//meta[@name = 'news_keywords']/@content").extract_first()
#             try:
#                 modified_video_keywords = [x.strip() for x in video_keywords.split(",")]
#             except:
#                 print("SPLIT ERROR")
#             keywords = Queries.insert_keywords(self, modified_video_keywords)
#             insertObject = {
#                 "video_title" : title,
#                 "video_slug" : slugify(title),
#                 "video_link" : video_url,
#                 "video_description" : description,
#                 "broadcaster" : "5d5b8ab011857574e9d440d2",
#                 "videoformat" : "5ce4f7ffa5c038104cb76649",
#                 "video_image" : image,
#                 "videokeywords" : keywords,
#                 "page_url" : response.url,
#                 "duration" : duration
#             }
#             result = Queries.insert_api(self, insertObject)
#             if result.status_code == 200:
#                 print("INSERTED")
#             else:
#                 print(result.status_code)
#                 print(result)
#         except:
#             print("URL MISSING")
