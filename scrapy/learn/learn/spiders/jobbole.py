# -*- coding: utf-8 -*-
import scrapy


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/']

    def parse(self, response):
        #response.xpath()返回的不是节点而是选择器，可以继续通过xpath来选取信息
        a = 'a'
        b = 'c'

        pass
