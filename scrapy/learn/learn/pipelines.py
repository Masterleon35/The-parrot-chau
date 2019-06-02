# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from twisted.internet import defer, reactor

class LearnPipeline(object):
    def process_item(self, item, spider):
        return item

class MongoPipeline():
    def __init__(self,crawler):
        self.mongo_uri = crawler.settings.get("MONGO_URI")
        self.mongo_db = crawler.settings.get("MONGO_DB")
        self.col = crawler.settings.get("MONGO_COL")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_uri,port = 27017)
        db = self.client.admin
        db.authenticate('litianhao', '19960812')
        self.db = self.client[self.mongo_db]

    #异步写法
    @defer.inlineCallbacks
    def process_item(self, item, spider):
        out = defer.Deferred()
        reactor.callInThread(self._insert, item, out)
        yield out
        defer.returnValue(item)

    def _insert(self, item, out):
        self.db[self.col].insert_one(dict(item))
        reactor.callFromThread(out.callback, item)

    # def process_item(self,item,spider):
    #       ''' 非异步'''
    #     # db = self.client.admin
    #     # db.authenticate('litianhao', '19960812')
    #     self.db[self.collection].insert_one(dict(item))
    #     return item

    def close_spider(self,spider):
        self.client.close()
    #可运行
    # def open_spider(self,spider):
    #     self.client = pymongo.MongoClient('localhost',port = 27017)
    #     db = self.client.admin
    #     db.authenticate('litianhao', '19960812')
    #     self.db = self.client['spider_info_haodafu']
    #
    # def process_item(self,item,spider):
    #     # db = self.client.admin
    #     # db.authenticate('litianhao', '19960812')
    #     self.db['spider_info_haodafu'].insert_one(item)
    #     return item
    #
    # def close_spider(self,spider):
    #     self.client.close()

