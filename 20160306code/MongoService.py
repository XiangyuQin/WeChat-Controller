# -*- coding: UTF-8 -*-
import pymongo
import common
from Log import Log
from pymongo import MongoClient

class MongoService(object):
    def __init__(self, log=None):
        self.log = log
        conn = MongoClient("localhost", 27017)
        self.db = conn["webSite"]
        
    def getArticles(self, type, limit, mark):
        cursor = self.getCursor(mark)
        cursor_doc = cursor.find({"type_id":type}).sort([("rankingScore", pymongo.ASCENDING),("date",pymongo.ASCENDING)]).limit(limit)
        array=[]
        for doc in cursor_doc:
            del doc["_id"]
            array.append(doc)
        return array
        
    def getCursor(self, mark):
        if mark=="A":
            cursor = self.db.articlesA
        else:
            cursor = self.db.articlesB
        return cursor
        
if __name__ == '__main__':
    now=datetime.datetime.now()
    log = Log(now)
    service = MongoService()
    dict =service.setArticles()
    print len(dict)
    print type(dict)

