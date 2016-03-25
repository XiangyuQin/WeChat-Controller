# -*- coding: UTF-8 -*-
import redis
import common
import datetime
from Log import Log

class RedisService(object):
    def __init__(self, log=None):
        self.r = redis.Redis(host='localhost', port=6379, db=0)
        self.log = log
            
    def getArticlesMark(self):
        try:
            mark = self.r.get("rankMark")
            return mark
        except Exception as e:
            self.log.printError("getArticlesMark:%s" %(e))
            return ""
            

if __name__ == '__main__':
    service = RedisService()
    