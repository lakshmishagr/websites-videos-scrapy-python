ż#WEB SCRAPING USING SCRAPY

1. Install scrapy command
2. Install dependencies like pymongo, slugify
3. Make sure python env is 3

#Web Scraping is already implemented for ABP, Pune Mirror, ZeeNews
(follow the same procedure for future links)

All news spiders are inside #Spiders folder.

Basic Illustration:-
    Lets trace ABP spider flow:-
    1. ABP spider is inside spider folder
    2. Run the scrapy crawl command using the spider identifier
    3. output the data to a json file to cross check

for single file crawl
ex: scrapy crawl page_bgr
inside Spiders folder all files are present, every file have class and here "name" value define file


you can set cron for all files, using index,index1,index2,index3 files

In Database folder "Database.py" have db connection
"Quieries.py" have db insert video details object

Here im use strapi with mongo-db has backend, and broadcastersvideos has table name and respective fileds 
{
   "video_title": title,
   "video_slug": slugify(title),
   "video_link": video_url,
   "video_description": description,
   "broadcaster": "5eda5e4e3a51c667efdcdf88",
   "videoformat": "5ce4f7eda5c038104cb76648",
   "video_image": image,
   "videokeywords": keywords,
   "page_url": response.url,
   "duration" : modified_time,
   "category": category,
   "language": "english",
   "keywords": ' | '.join(map(str, modified_video_keywords))
}
broadcaster,videoformat,videokeywords are relational tables
