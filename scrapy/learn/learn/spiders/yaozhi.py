# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from openpyxl import  load_workbook
import re
from lxml import etree
from learn.items import YaoZhiHospitalItem,YaoZhiClinicItem
import pymongo
import codecs
from urllib.parse import urljoin
import urllib
import pandas as pd
import logging

class YaozhiSpider(scrapy.Spider):
    name = 'yaozhi'
    # allowed_domains = ['https://db.yaozh.com/hmap']
    hospital_name_series = pd.read_excel('/Users/litianhao/Desktop/filebase/hospital-node_mapping_newest.xlsx',headers = None, skiprows = 5).loc[:, 'Unnamed: 0']
    start_urls = ['https://db.yaozh.com/hmap?name={}'.format(urllib.parse.quote(hospital_name.strip())) for hospital_name in hospital_name_series]
    # start_urls = ['https://db.yaozh.com/hmap?name={}'.format(urllib.parse.quote('首都医科大学宣武医院'))]
    # start_urls = ['https://db.yaozh.com/hmap?name=%E5%B9%BF%E5%B7%9E%E5%8C%BB%E7%A7%91%E5%A4%A7%E5%AD%A6%E9%99%84%E5%B1%9E%E7%AC%AC%E4%B8%80%E5%8C%BB%E9%99%A2']
    def parse(self, response):
        hospital_part_urls = response.xpath('//table[@class = "table table-striped"]//tr//a/@href').extract()
        if hospital_part_urls:
            hospital_comp_urls = [urljoin('https://db.yaozh.com/hmap',x) for x in hospital_part_urls]
            for hospital_url in hospital_comp_urls:
                params = urllib.parse.parse_qs(urllib.parse.urlparse(response.url).query)
                yield Request(url = hospital_url, callback = self.parse_hospital_detail, meta = {'hospital_yidu_name':params['name']} )
        else:
            with codecs.open('/Users/litianhao/Desktop/爬取日志/搜索返回结果为空_url.txt','a','utf8')as f:
                f.write(str(response.url)+'\n')

    def parse_hospital_detail(self,response):
        search_name = response.meta['hospital_yidu_name']
        # try:
        df_list = pd.read_html(response.body_as_unicode(),na_values='无', keep_default_na=True)
        # except:
        #     logging.warning('异常body##################')
        #     logging.warning(response.url)
        #     logging.warning(response.body_as_unicode())
        #     yield  Request(url = response.url, callback = self.parse_hospital_detail, meta = {'hospital_yidu_name':search_name} )
        # else:
        assert len(df_list) > 0, '没有解析出表格'
        hosiptial_info_dict = df_list[0].set_index(0).T.to_dict('records')
        information = YaoZhiHospitalItem()
        Clinic_part_url = response.xpath(
            '//div[@class = "other-database"]/a[@class = "btn btn-blue"]/@href').extract_first()
        if Clinic_part_url:
            Clinic_comp_url = urljoin('https://db.yaozh.com/hmap', Clinic_part_url)

            # middle_dic = {}
            # for x,y in hosiptial_info_dict.items():
            #     middle_dic[x] = y

            information['Detail_info'] = hosiptial_info_dict
            information['Response'] = response.body_as_unicode()
            information['Page_URL'] = response.url
            information['Search_name'] = search_name[0]
            information['Clinic_URL'] = Clinic_comp_url

            yield information
            yield Request(url = Clinic_comp_url, callback = self.parse_Clinic,
                          meta = {'hospital_yidu_name': search_name})
        else:
            # middle_dic = {}
            # for x,y in hosiptial_info_dict.items():
            #     middle_dic[x] = y

            information['Detail_info'] = hosiptial_info_dict
            information['Response'] = response.body_as_unicode()
            information['Page_URL'] = response.url
            information['Search_name'] = search_name[0]
            yield information



    def parse_Clinic(self,response):
        search_name = response.meta['hospital_yidu_name']

        clinic_part_urls = response.xpath('//table[@class = "table table-striped"]//tr//a[@class = "cl-blue"]/@href').extract()
        for clinic_part_url in clinic_part_urls:
            complete_url = urljoin('https://db.yaozh.com',clinic_part_url)
            yield Request(url = complete_url, callback = self.parse_Clinic_detail,meta = {'hospital_yidu_name':search_name})
        if '下一页' in response.xpath('//div[@class = "tr offset-top pagination"]/a/text()').extract():
            next_url_index = response.xpath('//div[@class = "tr offset-top pagination"]/a/text()').extract().index('下一页')
            next_url = response.xpath('//div[@class = "tr offset-top pagination"]/a/@href').extract()[next_url_index]
            completed_next_url = urljoin('https://db.yaozh.com',next_url)
            yield Request(url = completed_next_url,callback = self.parse_Clinic,meta = {'hospital_yidu_name':search_name})

    def parse_Clinic_detail(self,response):
        search_name = response.meta['hospital_yidu_name']

        df_list = pd.read_html(response.body_as_unicode(),na_values='无', keep_default_na=True)
        assert len(df_list) > 0, '没有解析出表格'
        clinic_info_dict = df_list[0].set_index(0).T.to_dict('records')
        information = YaoZhiClinicItem()
        # middle_dic = {}
        # for x,y in clinic_info_dict.items():
        #     middle_dic[x] = y
        information['Detail_info'] = clinic_info_dict
        information['Page_URL'] = response.url
        information['Search_name'] = search_name[0]

        yield information




