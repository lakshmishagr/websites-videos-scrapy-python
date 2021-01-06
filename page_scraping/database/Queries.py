from ..database.Database import Database
import json, pymongo, requests
from slugify import slugify
class Queries(object):
    _db_collection = Database.db.broadcastersvideos
    _db_collection_keywords = Database.db.video_keywords
    
    def insert_videos(self, object):
        # print(object)
        try:
            Queries._db_collection.insert_one(object)
        except pymongo.errors.DuplicateKeyError:
            print("Unique Keys encountered")

    def insert_keywords(self, keywords):
        keyword_list = []
        for keyword in keywords:
            try:
                insert = Queries._db_collection_keywords.insert({"name" : keyword, "slug": slugify(keyword)})
                keyword_list.append(insert)
                print('keyword inserted')
            except pymongo.errors.DuplicateKeyError:
                print("UNIQUE KEYWORD ERROR")
                try:
                    find = Queries._db_collection_keywords.find_one({"slug": slugify(keyword)})
                    keyword_list.append(find.get('_id'))
                except pymongo.errors.BulkWriteError as e:
                    print("BULK ERROR" + e)
        return keyword_list

    def insert_api(self, object):
        return requests.post('https://your-strapi-backend.com/broadcastersvideos', data=object)

#https://your-strapi-backend.com/broadcastersvideos of broadcastersvideos table