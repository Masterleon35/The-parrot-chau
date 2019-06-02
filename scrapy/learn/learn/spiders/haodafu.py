# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from openpyxl import  load_workbook
import re
from lxml import etree
from learn.items import HaodafuItem
import pymongo
import codecs
from urllib.parse import urljoin

class HaodafuSpider(scrapy.Spider):
    name = 'haodafu'
    # allowed_domains = ['https://www.haodf.com']
    all_sheet = load_workbook("/pycharm/行业知识图谱文件/医院种子数据.xlsx")
    start_urls = []
    for i in all_sheet['汇总']['B']:
        if i.value != None:
            start_urls.append(i.value)
    start_urls = [x.replace('.htm', '/menzhen.htm') for x in start_urls]
    # start_urls = ['https://www.haodf.com/hospital/DE4roiYGYZwmKnpHKRSoDWRPl/menzhen.htm']
    def parse(self, response):
        doctor_urls = response.xpath('//table[@id = "doc_list_index"]//li/a[@target = "_blank" and @class = "name"]/@href').extract()
        for post_url in doctor_urls:
            complete_url = urljoin('https:',post_url)
            yield Request(url = complete_url, callback = self.parse_detail)
        if '下一页' in response.xpath('//table//div[@class = "p_bar"]/a[@class = "p_num"]/text()').extract():
            next_url_index = response.xpath('//table//div[@class = "p_bar"]/a[@class = "p_num"]/text()').extract().index('下一页')
            next_url = response.xpath('//table//div[@class = "p_bar"]/a[@class = "p_num"]/@href').extract()[next_url_index]
            completed_next_url = urljoin('https:',next_url)
            yield Request(url = completed_next_url,callback = self.parse)

    def parse_detail(self,response):
        if not response.body_as_unicode:
            with codecs.open('/Users/litianhao/Desktop/爬取日志/response_body为空_url.txt','a','utf8')as f:
                f.write(str(response.url)+'\n')
        java_script = response.xpath('//script[@type = "text/javascript"]/text()').extract()
        unicode_inside_text1 = re.search('"content":"(.+)","cssList"', java_script[1]).group(
            1)  # 包含医生所属地区医院等信息但是其为unicode编码的字符
        unicode_inside_text2 = re.search('"content":"(.+)","cssList"', java_script[2]).group(
            1)  # 包含医生简介职称评分满意度等信息但是其为的unicode编码的字符
        normal_display_text1 = unicode_inside_text1.replace('\\/', '/').replace('\\n', '\n').replace('\\"',
                                                                                                     '"').replace('\\t',
                                                                                                                  '\t')
        # 处理html中双转义符
        normal_display_text2 = unicode_inside_text2.replace('\\/', '/').replace('\\n', '\n').replace('\\"',
                                                                                                     '"').replace('\\t',
                                                                                                                  '\t')
        # 处理html中的双转义符
        need_analysis_js1 = normal_display_text1.encode().decode("unicode_escape")  # 将unicode编码的字符转化为汉字显示
        need_analysis_js2 = normal_display_text2.encode().decode("unicode_escape")  # 将unicode编码的字符转化为汉字显示
        analysised_html1 = etree.HTML(need_analysis_js1)
        analysised_html2 = etree.HTML(need_analysis_js2)

        #基本信息
        province, hospital, department, name = analysised_html1.xpath('//div[@class = "luj"]/a/text()')[2:6]

        #职称
        title_index = analysised_html2.xpath('//div[@class = "lt"]//tr/td/text()').index('职\u3000\u3000称：') + 1
        title = analysised_html2.xpath('//div[@class = "lt"]//tr/td/text()')[title_index]

        #介绍TODO
        introduction_list = analysised_html2.xpath('//div[@class = "lt"]//tr/td/div[@id = "full"]/text()')
        introduction_list1 = analysised_html2.xpath(
            '//div[@class = "lt"]//tr/td[@colspan = "3" and @valign = "top"]/text()')
        if introduction_list:
            length = len(introduction_list)
            introduction = ''
            for index in range(length):
                introduction += introduction_list[index].strip()
        elif introduction_list1:
            length = len(introduction_list1)
            introduction = ''
            for index in range(length):
                introduction += introduction_list1[index].strip()
        else:
            introduction = ''

        #擅长
        be_good_at_list = analysised_html2.xpath(
            '//div[@class = "lt"]//tr/td/div[@id = "full_DoctorSpecialize"]/text()')
        be_good_at_list1 = analysised_html2.xpath(
            '//div[@class = "lt"]//tr/td/div[@id = "truncate_DoctorSpecialize"]/text()')
        if be_good_at_list:
            length = len(be_good_at_list)
            be_good_at = ''
            for index in range(length):
                be_good_at += be_good_at_list[index].strip()
        elif introduction_list1:
            length = len(be_good_at_list1)
            be_good_at = ''
            for index in range(length):
                be_good_at += be_good_at_list1[index].strip()
        else:
            be_good_at = ''
        #得分表
        score_list = analysised_html2.xpath('//p[@class="r-p-l-score"]/text()')
        if score_list:
            score = score_list[0].strip()
        else:
            score = ''

        #回复信息列表
        question_reply_numbers_list = analysised_html2.xpath('//span[@class="orange"]/text()')
        if question_reply_numbers_list:
            question_number = question_reply_numbers_list[0]
            reply_number = question_reply_numbers_list[1]
        else:
            question_number = ''
            reply_number = ''
        satisfaction_number_from_patient = analysised_html2.xpath('//div[@class = "fl score-part"]/p/span/text()')
        satisfaction_number_from_patient = [x.split('：')[1] for x in satisfaction_number_from_patient]

        #特需
        unique = response.xpath('//td[@class = "midmd"]//span[@class = "unique"]/@title').extract_first()
        boolean = 'False'
        if unique:
            boolean = 'True'

        information = HaodafuItem()
        information['BasicInfo'] = {
            'Name':name,
            'ProfessionalTitleAndRank':title,
            'haodafuWB':{
                'url':response.url,
                'score':score,
                'DegreeSatifactionCuraiveEffect': satisfaction_number_from_patient[0],
                'DegreeSatifactionAttitude': satisfaction_number_from_patient[2],
                'addupHlepPatientNumber': satisfaction_number_from_patient[1],
                'nearlyHlepPatientNumber' : satisfaction_number_from_patient[3],
                'patientQuestionNumber' : question_number,
                'doctorAnsweredNumber': reply_number
            },
            'TODO':introduction,
            'BeGoodAt':be_good_at,
            'Hospital' : hospital,
            'Department' : department,
            'Unique': boolean,
            'Response' : response.body_as_unicode()
        }
        # information["SocialMeida"] = {}
        # information["SocialMeida"]['haodafuWB'] = {}
        # information['BasicInfo']['Name'] = name
        # information['BasicInfo']['ProfessionalTitleAndRank'] = title
        # information['TODO'] = introduction
        # information['BasicInfo']['BeGoodAt'] = be_good_at
        # information["SocialMeida"]['haodafuWB']['score'] = score
        # information["SocialMeida"]['haodafuWB']['DegreeSatifactionCuraiveEffect'] = satisfaction_number_from_patient[0]
        # information["SocialMeida"]['haodafuWB']['DegreeSatifactionAttitude'] = satisfaction_number_from_patient[2]
        # information["SocialMeida"]['haodafuWB']['addupHlepPatientNumber'] = satisfaction_number_from_patient[1]
        # information["SocialMeida"]['haodafuWB']['nearlyHlepPatientNumber'] = satisfaction_number_from_patient[3]
        # information["SocialMeida"]['haodafuWB']['patientQuestionNumber'] = question_number
        # information["SocialMeida"]['haodafuWB']['doctorAnsweredNumber'] = reply_number
        # information['Hospital'] = hospital
        # information['Department'] = department
        yield information