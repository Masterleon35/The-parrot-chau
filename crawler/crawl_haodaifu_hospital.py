import requests
from lxml import etree
from xpinyin import Pinyin

def get_ProvinceName_list(url = 'https://www.haodf.com/yiyuan/all/list.htm'):
	'''
	通过全国医院首页获取省份名称，以便后续获取各个省份的特定的url
	:param url:全国医院首页的url
	:return:一个列表，包含全国所有省份名称
	'''
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
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
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
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
#%%
def get_LongIntroductionPage_MapPage_url(one_hospital_url):
	'''
	通过医院页面的url得到医院介绍和医院地址的两个页面url
	:param one_hospital_url: 单个医院的url
	:return:一个元祖，包含一个医院页面的两个子链接的url，分别是医院的长文本介绍和医院地址信息。
	'''
	ns = {"re": "http://exslt.org/regular-expressions"}#正则要用到
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
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
	return (LongIntroductionPage_url, MapPage_url,address_info)


#%%
get_LongIntroductionPage_MapPage_url('https://www.haodf.com//hospital/DE4raCNSz6OmG3OUNZWCWNv0.htm')
get_LongIntroductionPage_MapPage_url('https://www.haodf.com//hospital/DE4r0Fy0C9Luw0JbbOYM5tQ4z9ZEju-cx.htm')
#%%
def get_one_hospital_info(one_hospital_url):
	'''有bug'''
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
	one_hospital_html = requests.get(one_hospital_url,headers = headers)
	LongIntroductionURL,MapURL,adress_info = get_LongIntroductionPage_MapPage_url(one_hospital_url)
	LongIntroduction_html = requests.get(LongIntroductionURL,headers = headers)
	Map_html = requests.get(MapURL,headers = headers)
	LongIntroduction_html_analysis = etree.HTML(LongIntroduction_html.text)
	Map_html_analysis = etree.HTML(Map_html.text)
	Hospital_name = LongIntroduction_html_analysis.xpath("//div[@id='headpA_blue']//a/text()")
	Hospital_Introduction = LongIntroduction_html_analysis.xpath("//table[@class='czsj']//td/text()")
	return Hospital_name,Hospital_Introduction

#%%
get_one_hospital_info('https://www.haodf.com//hospital/DE4r0Fy0C9Luw0JbbOYM5tQ4z9ZEju-cx.htm')
#%%
if __name__ == '__main__':
	ProvinceNmae_list = get_ProvinceName_list()
	Province_hospital_dic = {}
	for ProvinceName in ProvinceNmae_list:
		Province_hospital_dic[ProvinceName] = get_all_hospital_url_from_one_province('https://www.haodf.com/yiyuan/all/list.htm',ProvinceName)
	print(Province_hospital_dic.values())
#%%
print(Province_hospital_dic.keys())

