# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LearnItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class HaodafuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    BasicInfo = scrapy.Field()
    SocialMeida = scrapy.Field()
    TODO = scrapy.Field()
    Hospital = scrapy.Field()
    Department = scrapy.Field()
    Reponse = scrapy.Field()
    Unique = scrapy.Field()
    # BasicInfo = scrapy.Field()
    pass

class YaoZhiHospitalItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Detail_info = scrapy.Field()
    Search_name = scrapy.Field()
    Response = scrapy.Field()
    Page_URL = scrapy.Field()
    Clinic_URL = scrapy.Field()

class YaoZhiClinicItem(scrapy.Item):
    Detail_info = scrapy.Field()
    Page_URL = scrapy.Field()
    Search_name = scrapy.Field()



    # BasicInfo = scrapy.Field()