import requests
from lxml import etree
from xpinyin import Pinyin
from fake_useragent import UserAgent
import random
import pymongo
import time
import codecs
from openpyxl import load_workbook

def get_ProvinceName_list(url = 'https://www.haodf.com/yiyuan/all/list.htm'):
	'''
	通过全国医院首页获取省份名称，以便后续获取各个省份的特定的url
	:param url:全国医院首页的url
	:return:一个列表，包含全国所有省份名称
	'''
	headers = {'User-Agent': UserAgent().random}
	html = requests.get(url, headers = headers)
	analysis_hospital_page = etree.HTML(html.text)
	province_name_list = analysis_hospital_page.xpath('//div[@class = "kstl"]/a/text()')  # 得到全国各个省市名单
	province_name_list.insert(0,'北京')
	return  province_name_list

def get_all_hospital_url_from_one_province(base_url,ProvinceName):
	'''
	将base_url和ProvinceName结合生成某一省份医院页面的url，然后再爬取所有该省份所有医院的url。
	:param base_url: 全国医院首页的url
	:param ProvinceName: 字符串，一个省份的名称
	:return:一个列表，该省份所有医院的url
	'''
	headers = {'User-Agent': UserAgent().random}
	ProvinceName_pinyin = Pinyin().get_pinyin(ProvinceName,"")
	ProvinceHospitalUrl = base_url.replace('all', ProvinceName_pinyin)
	if ProvinceName == '西藏':
		ProvinceName_pinyin = 'xizang'
	all_Province_hospital_html = requests.get(ProvinceHospitalUrl, headers = headers)
	all_Province_hospital_html_analysis = etree.HTML(all_Province_hospital_html.text)
	all_Province_hospital_url_list = all_Province_hospital_html_analysis.xpath(
		'//div[@class="ct"]/div[@class="m_ctt_green"]/ul/li/a/@href')
	# all_Province_hospital_class_and_rank_list = all_Province_hospital_html_analysis.xpath(
	# 	'//div[@class="ct"]/div[@class="m_ctt_green"]/ul/li/span/text()')
	all_Province_hospital_url_list = ['https://www.haodf.com/' + x for x in all_Province_hospital_url_list]
	# all_Province_hospital_class_and_rank_list = [x.strip() for x in all_Province_hospital_class_and_rank_list]
	# url_rank_class_info = zip(all_Province_hospital_url_list, all_Province_hospital_class_and_rank_list)
	return all_Province_hospital_url_list

def get_LongIntroductionPage_url(one_hospital_url):
	'''
	通过医院页面的url得到医院介绍和医院地址的两个页面url
	:param one_hospital_url: 单个医院的url
	:return:一个元祖，包含一个医院页面的两个子链接的url，分别是医院的长文本介绍和医院地址信息。
	'''
	ns = {"re": "http://exslt.org/regular-expressions"}#正则要用到
	proxy = random.choice(proxy_list)
	proxies = {
		'http': 'http://' + proxy,
		'https': 'https://' + proxy,
	}
	headers = {'User-Agent': UserAgent().random}
	one_hospital_html = requests.get(one_hospital_url,headers = headers)
	one_hospital_html_analysis = etree.HTML(one_hospital_html.text)
	LongIntroductionPage_url = one_hospital_url.replace('.htm','/jieshao.htm',1).replace('www','info',1)
	MapPage_url = one_hospital_html_analysis.xpath(
		'//div[@class="h-d-content"]/p[@class="h-d-c-item"]/a[@class="h-d-c-item-link" and re:match(@href,"//map\.haodf\.com.+")]/@href',
		namespaces = ns)
	if MapPage_url :
		MapPage_url = 'https:'+MapPage_url[0]
		address_info = ''
	else:
		address_info = one_hospital_html_analysis.xpath(
		'//div[@class="h-d-content"]/p[@class="h-d-c-item"]/span[@class="h-d-c-item-text"]/text()')[1]
	return LongIntroductionPage_url,MapPage_url,address_info


def get_one_hospital_info(one_hospital_url):
	''''''
	headers = {'User-Agent': UserAgent().random}
	one_hospital_html = requests.get(one_hospital_url,headers = headers,proxies = proxies,timeout = 4)
	one_hospital_html_analysised = etree.HTML(one_hospital_html.text)
	hospital_name = one_hospital_html_analysised.xpath('//h1[@class = "hospital-name"]/text()')[0]
	label = one_hospital_html_analysised.xpath('//span[@class = "hospital-label-item"]/text()')
	if len(label)>=2:
		Degree,Type = label[:2]
	elif len(label) == 1:
		Degree = label[0]
		Type = ''
	else:
		Degree,Type = ['','']

	PrimaryDepartment = one_hospital_html_analysised.xpath('//div[@class = "f-l-i-name"]/text()')
	SecondaryDepartment = one_hospital_html_analysised.xpath('//ul[@class = "f-l-i-second"]')
	SecondaryDepartment = [etree.HTML(bytes(etree.tostring(x))).xpath('//a[@class = "f-l-i-s-i-w-name"]/text()') for x in SecondaryDepartment]


	LongIntroductionURL,MapURL,address_info = get_LongIntroductionPage_url(one_hospital_url)
	if LongIntroductionURL:
		LongIntroduction_html = requests.get(LongIntroductionURL,headers = headers,proxies = proxies)
		LongIntroduction_html_analysis = etree.HTML(LongIntroduction_html.text)
		Hospital_Introduction = LongIntroduction_html_analysis.xpath("//table[@class='czsj']//td/text()")
	if MapURL:
		Map_html = requests.get(MapURL,headers = headers,proxies = proxies)
		Map_html_analysis = etree.HTML(Map_html.text)
		address_info = Map_html_analysis.xpath('//table//td[@valign = "top"]/text()')[4]

	hospital_info = {
		"NameCn":hospital_name,
		"Summary":Hospital_Introduction,
		"Address":address_info,
		"Degree":Degree,
		"Type":Type,
		"DepartmentStructure":[
			dict(zip(PrimaryDepartment, SecondaryDepartment))
		]

	}

	if collection_hospital.find_one({'NameCn': hospital_info['NameCn'], 'Address': hospital_info['Address']}):
		pass
		#                 print(str(index)+'重复',end = ',')
	else:
		collection_hospital.insert_one(hospital_info)
	# return hospital_info

def get_proxy_list(file_path = '/Users/litianhao/Desktop/ip池/ip.txt'):
	proxy_list = []
	with codecs.open(file_path,'r','utf8')as f:
		for line in f:
			proxy_list.append(line.strip())
	return proxy_list

if __name__ == "__main__":
	ua = UserAgent()
	client = pymongo.MongoClient(host = 'localhost', port = 27017)
	db = client.admin
	db.authenticate('litianhao', '19960812')
	mydb = client["spider_info_haodafu"]
	collection_hospital = mydb.hospital
	proxy_list = get_proxy_list()

	all_sheet = load_workbook("/Users/litianhao/Desktop/知识图谱数据/医院种子数据.xlsx")
	hospital_info_url=[]
	for i in all_sheet['汇总']['B']:
		if i.value != None:
			hospital_info_url.append(i.value)

	hospital_num = 0
	shenjing_2_flag = 0
	while hospital_num<152:
		proxy = random.choice(proxy_list)
		proxies = {
			'http': 'http://' + proxy,
			'https': 'https://' + proxy,
		}
		try:
			get_one_hospital_info(hospital_info_url[hospital_num])
		except IndexError:
			print('犯神经了',end = ',')
		except AttributeError:
			pass
		except ConnectionError:
			pass
			print('连接错误',end = ',')
		except requests.exceptions.Timeout:
			print('ip问题,删之',end = ',')
			if proxy in proxy_list:
				proxy_list.remove(proxy)
		except requests.exceptions.ConnectionError:
			print('ip被封,删之',end = ',')
			if proxy in proxy_list:
				proxy_list.remove(proxy)
		else:
			print('完成'+str(hospital_num),end = ',')
			hospital_num+=1



