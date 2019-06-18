# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from twisted.internet import defer, reactor
from learn.items import YaoZhiHospitalItem,YaoZhiClinicItem

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
        if isinstance(item, YaoZhiHospitalItem):
            reactor.callInThread(self._insert, item, out)
        # reactor.callInThread(self._insert, item, out)
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

class MongoPipeline1():
    def __init__(self, crawler):
        self.mongo_uri = crawler.settings.get("MONGO_URI")
        self.mongo_db = crawler.settings.get("MONGO_DB")
        self.col = crawler.settings.get("MONGO_COL_CLN")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri, port = 27017)
        db = self.client.admin
        db.authenticate('litianhao', '19960812')
        self.db = self.client[self.mongo_db]

        # 异步写法
    @defer.inlineCallbacks
    def process_item(self, item, spider):
        out = defer.Deferred()
        if isinstance(item, YaoZhiClinicItem):
            reactor.callInThread(self._insert, item, out)
            yield out
        defer.returnValue(item)

    def _insert(self, item, out):
        self.db[self.col].insert_one(dict(item))
        reactor.callFromThread(out.callback, item)


    def close_spider(self, spider):
        self.client.close()



