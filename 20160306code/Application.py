# -*- coding:utf-8 -*-
import datetime
from WeChatController import WeChatController
from MongoService import MongoService
from RedisService import RedisService
from Log import Log
import config

class Application(object):
    def __init__(self):
        self.now = datetime.datetime.now()
        self.log = Log(self.now)
        self.weChatController = WeChatController(logger=self.log)
        
    def run(self):
        self.SendMass()
        
    def SendMass(self):
        articles=self.getArticles("0", 1)
        appMsgs=self.generateMsgs(articles)
        self.weChatController.sendMass(appMsgs)
    
    def addAppMsg(self):
        articles=self.getArticles("1", 2)
        appMsgs=self.generateMsgs(articles)
        self.weChatController.addAppmsg(appMsgs)
        
    def SendAppmsg(self):
        articles=self.getArticles("1", 2)
        appMsgs=self.generateMsgs(articles)
        self.weChatController.sendAppmsg(config.test_tokenId2,appMsgs)
        
    def getArticles(self, type, limit):
        redisService = RedisService(self.log)
        mark = redisService.getArticlesMark()
        service = MongoService(self.log)
        articles = service.getArticles(type, limit, mark)
        return articles
        
    def generateMsgs(self,articles):
        appMsgs=[]
        for article in articles:
            appMsg = self.generateMsg(article)
            appMsgs.append(appMsg)  
        return appMsgs
        
    def generateMsg(self, article):
        appMsg={}
        appMsg["author"] = article["writer"]
        appMsg["title"] = article["title"]
        appMsg["sourceurl"] = "www.baidu.com"
        appMsg["cover"] = config.imageSrc+article["image"]
        appMsg["digest"] = article["brief"]
        appMsg["content"] = article["content"]
        return appMsg
        
    def uploadImg(self):
        imgUrl=""
        self.weChatController.uploadImg(imgUrl)
        
    def uploadArticles(self):
        articles=self.getArticles("0", 2)
        appMsgs=self.generateMsgs(articles)
        #print appMsgs
        self.weChatController.addAppmsg(appMsgs)
        
if __name__ == '__main__':
    application = Application()
    application.run() 