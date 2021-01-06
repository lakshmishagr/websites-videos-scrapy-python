from pymongo import MongoClient

class Database(object):

   # _client = MongoClient('mongodb://root:admin@localhost', 27017)
   _client = MongoClient(
           host='',
           port=27017,
           username='',
           password='',
           authSource='')
   db = _client['']
