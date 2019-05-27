import requests
from lxml import etree
import re
import codecs
import time
import pymongo
import sys
from fake_useragent import UserAgent
import random
from tqdm import tqdm
from multiprocessing import Pool
# -*-coding:utf-8 -*-
#%%
def get_department_url(url = 'https://www.haodf.com/'):
	'''
	:param url: 好大夫首页url
	:return: 一个列表包含各个科室页面的url
	'''
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
	html = requests.get(url, headers = headers)
	analysis_html = etree.HTML(html.text)
	ns = {"re": "http://exslt.org/regular-expressions"}
	keshi_url = analysis_html.xpath('//div[@class = "menu_con J_content"]'
	                        '/descendant::a[re:match(@href,"//www\.haodf\.com/keshi.+")]/@href',namespaces = ns)
	return ['https:'+url for url in keshi_url]

def get_allDoctorPage_url_of_departmentList(department_url):
	'''
	:param department_url:科室网页的url列表
	:return:一个列表，包含各个科室的所有医生页面的url
	'''
	all_doctorpage_url = []
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
	for url in department_url:
		html = requests.get(url, headers = headers)
		str_url = str(html.url)
		str_url = str_url.replace('www', 'haoping')
		str_url = str_url.replace('.htm', '/daifu_all.htm')
		all_doctorpage_url.append(str_url)
		time.sleep(0.1)
	return  all_doctorpage_url

def get_30_doctor_url_from_alldoctor_page(all_doctor_page_url):
	'''
	:param all_doctor_page_url:包含30个医生页面的url
	:return:返回一个长度为30的列表。每个医生个人主页的url
	'''
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
	html_plus = requests.get(all_doctor_page_url, headers = headers)
	analysis_html = etree.HTML(html_plus.text)
	ns = {"re": "http://exslt.org/regular-expressions"}

	doctor_url = analysis_html.xpath(
		'//a[re:match(@href,"//www\.haodf\.com/doctor.+") and @target = "_blank" and @class = "blue"]/@href',
		namespaces = ns)
	return ['https:'+url for url in doctor_url]

def get_all_doctor_url_from_all_pages_one_department(base_url):
	'''
	 :param base_url: 包含30个医生的第一页的url
	 :return: 返回一个生成器。其内容是一个字典，字典的键为页面值，字典的值为该页面30个医生个人主页的url
	 '''
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
	all_doctor_list = []
	html_plus = requests.get(base_url, headers = headers)
	analysis_html = etree.HTML(html_plus.text)
	pages_num_raw = analysis_html.xpath('//a[@class = "p_text" and @rel = "true"]/text()')
	if pages_num_raw:
		pages_num = pages_num_raw[0].split('\xa0')[1]
	else:
		pages_num = 1
	all_doctor_list.extend(get_30_doctor_url_from_alldoctor_page(base_url))
	html_for_get_regular_url = requests.get(base_url, headers = headers)
	base_url = str(html_for_get_regular_url.url)
	for page_num in tqdm(range(2, int(pages_num))):
		flag = True
		while flag:
			#  with Pool() as pool:
			#   all_doctor_list[page_num] = pool.map(get_30_doctor_url_from_alldoctor_page,base_url.replace('.htm','_'+str(page_num)+'.htm'))
			url30 = get_30_doctor_url_from_alldoctor_page(base_url.replace('.htm', '_' + str(page_num) + '.htm'))
			time.sleep(0.1)
			if len(url30) < 30:
				pass
			else:
				flag = False
				all_doctor_list.extend(url30)
	all_doctor_list.extend(get_30_doctor_url_from_alldoctor_page(base_url.replace('.htm', '_' + str(pages_num) + '.htm')))
	yield all_doctor_list

def get_one_doctor_info(doctor_page_url,proxy):
    headers = {'User-Agent': ua.random}
    proxies = {
            'http': 'http://' + proxy,
            'https': 'https://' + proxy,
            }
    html = requests.get(doctor_page_url, headers = headers,proxies=proxies,timeout = 5)
    time.sleep(0.1)
    doctor_page_analysis = etree.HTML(html.text)
    java_script = doctor_page_analysis.xpath('//script[@type = "text/javascript"]/text()')
    unicode_inside_text1 = re.search('"content":"(.+)","cssList"', java_script[1]).group(1)#包含医生所属地区医院等信息但是其为unicode编码的字符
    unicode_inside_text2 = re.search('"content":"(.+)","cssList"', java_script[2]).group(1)#包含医生简介职称评分满意度等信息但是其为的unicode编码的字符
    normal_display_text1 = unicode_inside_text1.replace('\\/', '/').replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
        #处理html中双转义符
    normal_display_text2 = unicode_inside_text2.replace('\\/', '/').replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
        #处理html中的双转义符
    need_analysis_js1 = normal_display_text1.encode().decode("unicode_escape")#将unicode编码的字符转化为汉字显示
    need_analysis_js2 = normal_display_text2.encode().decode("unicode_escape")#将unicode编码的字符转化为汉字显示
    analysised_html1 = etree.HTML(need_analysis_js1)
    analysised_html2 = etree.HTML(need_analysis_js2)
    province,hospital,department,name = analysised_html1.xpath('//div[@class = "luj"]/a/text()')[2:6]
    title_index = analysised_html2.xpath('//div[@class = "lt"]//tr/td/text()').index('职\u3000\u3000称：')+1
    title = analysised_html2.xpath('//div[@class = "lt"]//tr/td/text()')[title_index]
    introduction_list = analysised_html2.xpath('//div[@class = "lt"]//tr/td/div[@id = "full"]/text()')
    introduction_list1 = analysised_html2.xpath('//div[@class = "lt"]//tr/td[@colspan = "3" and @valign = "top"]/text()')
    if introduction_list:
        length = len(introduction_list)
        introduction = ''
        for index in range(length):
            introduction+=introduction_list[index].strip()
    elif introduction_list1:
        length = len(introduction_list1)
        introduction = ''
        for index in range(length):
            introduction += introduction_list1[index].strip()
    else:introduction = ''
    be_good_at_list = analysised_html2.xpath('//div[@class = "lt"]//tr/td/div[@id = "full_DoctorSpecialize"]/text()')
    be_good_at_list1 = analysised_html2.xpath('//div[@class = "lt"]//tr/td/div[@id = "truncate_DoctorSpecialize"]/text()')
    if be_good_at_list:
        length = len(be_good_at_list)
        be_good_at = ''
        for index in range(length):
            be_good_at+=be_good_at_list[index].strip()
    elif introduction_list1:
        length = len(be_good_at_list1)
        be_good_at = ''
        for index in range(length):
            be_good_at += be_good_at_list1[index].strip()
    else:be_good_at = ''
    score_list = analysised_html2.xpath('//p[@class="r-p-l-score"]/text()')
    if score_list:
        score = score_list[0].strip()
    else:score = ''
    question_reply_numbers_list = analysised_html2.xpath('//span[@class="orange"]/text()')
    if question_reply_numbers_list:
        question_number = question_reply_numbers_list[0]
        reply_number = question_reply_numbers_list[1]
    else:
        question_number = ''
        reply_number = ''
    satisfaction_number_from_patient = analysised_html2.xpath('//div[@class = "fl score-part"]/p/span/text()')
    satisfaction_number_from_patient = [x.split('：')[1] for x in satisfaction_number_from_patient]
    information = {}
    information['BasicInfo'] = {}
    information["SocialMeida"] = {}
    information["SocialMeida"]['haodafuWB'] = {}
    information['BasicInfo']['Name'] = name
    information['BasicInfo']['ProfessionalTitleAndRank'] = title
    information['TODO'] = introduction
    information['BasicInfo']['BeGoodAt'] = be_good_at
    information["SocialMeida"]['haodafuWB']['score'] = score
    information["SocialMeida"]['haodafuWB']['DegreeSatifactionCuraiveEffect'] = satisfaction_number_from_patient[0]
    information["SocialMeida"]['haodafuWB']['DegreeSatifactionAttitude'] = satisfaction_number_from_patient[2]
    information["SocialMeida"]['haodafuWB']['addupHlepPatientNumber'] = satisfaction_number_from_patient[1]
    information["SocialMeida"]['haodafuWB']['nearlyHlepPatientNumber'] = satisfaction_number_from_patient[3]
    information["SocialMeida"]['haodafuWB']['patientQuestionNumber'] = question_number
    information["SocialMeida"]['haodafuWB']['doctorAnsweredNumber'] = reply_number
    information['Hospital'] = hospital
    information['Department'] = department
    return information

def get_doctorinfo_pushin_mangoDB(emergency_alldoctor_url_notchongfu):
    index = 0
    shenjing_2_flag = 0
    while index<len(emergency_alldoctor_url_notchongfu):
        proxy = random.choice(proxy_list)# 随机从ip池中选出一个ip
        try:
            doctor_info = get_one_doctor_info(emergency_alldoctor_url_notchongfu[index],proxy)
            time.sleep(0.1)
        except IndexError:
#             print('ip用完了',index,end = ',')
            break
        except AttributeError:
#             print('神经了2',end = ',')
            shenjing_2_flag+=1
            if shenjing_2_flag>3:
                shenjing_2_flag = 0
                index+=1
        except ConnectionError:
            pass
#             print('连接错误',end = ',')
        except requests.exceptions.Timeout:
#             print('ip问题,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        except requests.exceptions.ConnectionError:
#             print('ip被封,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        else:
            index+=1
            if collection.find_one({'BasicInfo': doctor_info['BasicInfo'],'Hospital': doctor_info['Hospital']}):
                pass
#                 print(str(index)+'重复',end = ',')
            else:
                collection.insert_one(doctor_info)
#                 print(index,end = ',')

def get_doctorinfo_pushin_mangoDB1(x):
    index = 0
    shenjing_2_flag = 0
    while index<len(doctor_url_notchongfu1):
        proxy = random.choice(proxy_list)# 随机从ip池中选出一个ip
        try:
            doctor_info = get_one_doctor_info(doctor_url_notchongfu1[index], proxy)
            time.sleep(0.1)
        except IndexError:
#             print('ip用完了',index,end = ',')
            break
        except AttributeError:
#             print('神经了2',end = ',')
            shenjing_2_flag+=1
            if shenjing_2_flag>3:
                shenjing_2_flag = 0
                index+=1
        except ConnectionError:
            pass
#             print('连接错误',end = ',')
        except requests.exceptions.Timeout:
#             print('ip问题,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        except requests.exceptions.ConnectionError:
#             print('ip被封,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        else:
            index+=1
            if collection.find_one({'BasicInfo': doctor_info['BasicInfo'],'Hospital': doctor_info['Hospital']}):
                pass
#                 print(str(index)+'重复',end = ',')
            else:
                result = collection.insert_one(doctor_info)
#                 print(index,end = ',')

def get_doctorinfo_pushin_mangoDB2(x):
    index = 0
    shenjing_2_flag = 0
    while index<len(doctor_url_notchongfu2):
        proxy = random.choice(proxy_list)# 随机从ip池中选出一个ip
        try:
            doctor_info = get_one_doctor_info(doctor_url_notchongfu2[index], proxy)
            time.sleep(0.1)
        except IndexError:
#             print('ip用完了',index,end = ',')
            break
        except AttributeError:
#             print('神经了2',end = ',')
            shenjing_2_flag+=1
            if shenjing_2_flag>3:
                shenjing_2_flag = 0
                index+=1
        except ConnectionError:
            pass
#             print('连接错误',end = ',')
        except requests.exceptions.Timeout:
#             print('ip问题,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        except requests.exceptions.ConnectionError:
#             print('ip被封,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        else:
            index+=1
            if collection.find_one({'BasicInfo': doctor_info['BasicInfo'],'Hospital': doctor_info['Hospital']}):
                pass
#                 print(str(index)+'重复',end = ',')
            else:
                result = collection.insert_one(doctor_info)
#                 print(index,end = ',')

def get_doctorinfo_pushin_mangoDB3(x):
    index = 0
    shenjing_2_flag = 0
    while index<len(doctor_url_notchongfu3):
        proxy = random.choice(proxy_list)# 随机从ip池中选出一个ip
        try:
            doctor_info = get_one_doctor_info(doctor_url_notchongfu3[index], proxy)
            time.sleep(0.1)
        except IndexError:
#             print('ip用完了',index,end = ',')
            break
        except AttributeError:
#             print('神经了2',end = ',')
            shenjing_2_flag+=1
            if shenjing_2_flag>3:
                shenjing_2_flag = 0
                index+=1
        except ConnectionError:
            pass
#             print('连接错误',end = ',')
        except requests.exceptions.Timeout:
#             print('ip问题,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        except requests.exceptions.ConnectionError:
#             print('ip被封,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        else:
            index+=1
            if collection.find_one({'BasicInfo': doctor_info['BasicInfo'],'Hospital': doctor_info['Hospital']}):
                pass
#                 print(str(index)+'重复',end = ',')
            else:
                result = collection.insert_one(doctor_info)
#                 print(index,end = ',')

def get_doctorinfo_pushin_mangoDB4(x):
    index = 0
    shenjing_2_flag = 0
    while index<len(doctor_url_notchongfu4):
        proxy = random.choice(proxy_list)# 随机从ip池中选出一个ip
        try:
            doctor_info = get_one_doctor_info(doctor_url_notchongfu4[index], proxy)
            time.sleep(0.1)
        except IndexError:
#             print('ip用完了',index,end = ',')
            break
        except AttributeError:
#             print('神经了2',end = ',')
            shenjing_2_flag+=1
            if shenjing_2_flag>3:
                shenjing_2_flag = 0
                index+=1
        except ConnectionError:
            pass
#             print('连接错误',end = ',')
        except requests.exceptions.Timeout:
#             print('ip问题,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        except requests.exceptions.ConnectionError:
#             print('ip被封,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        else:
            index+=1
            if collection.find_one({'BasicInfo': doctor_info['BasicInfo'],'Hospital': doctor_info['Hospital']}):
                pass
#                 print(str(index)+'重复',end = ',')
            else:
                result = collection.insert_one(doctor_info)
#                 print(index,end = ',')

def get_doctorinfo_pushin_mangoDB5(x):
    index = 0
    shenjing_2_flag = 0
    while index<len(doctor_url_notchongfu5):
        proxy = random.choice(proxy_list)# 随机从ip池中选出一个ip
        try:
            doctor_info = get_one_doctor_info(doctor_url_notchongfu5[index], proxy)
            time.sleep(0.1)
        except IndexError:
#             print('ip用完了',index,end = ',')
            break
        except AttributeError:
#             print('神经了2',end = ',')
            shenjing_2_flag+=1
            if shenjing_2_flag>3:
                shenjing_2_flag = 0
                index+=1
        except ConnectionError:
            pass
#             print('连接错误',end = ',')
        except requests.exceptions.Timeout:
#             print('ip问题,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        except requests.exceptions.ConnectionError:
#             print('ip被封,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        else:
            index+=1
            if collection.find_one({'BasicInfo': doctor_info['BasicInfo'],'Hospital': doctor_info['Hospital']}):
                pass
#                 print(str(index)+'重复',end = ',')
            else:
                result = collection.insert_one(doctor_info)
#                 print(index,end = ',')

def get_doctorinfo_pushin_mangoDB6(x):
    index = 0
    shenjing_2_flag = 0
    while index<len(doctor_url_notchongfu6):
        proxy = random.choice(proxy_list)# 随机从ip池中选出一个ip
        try:
            doctor_info = get_one_doctor_info(doctor_url_notchongfu6[index], proxy)
            time.sleep(0.1)
        except IndexError:
#             print('ip用完了',index,end = ',')
            break
        except AttributeError:
#             print('神经了2',end = ',')
            shenjing_2_flag+=1
            if shenjing_2_flag>3:
                shenjing_2_flag = 0
                index+=1
        except ConnectionError:
            pass
#             print('连接错误',end = ',')
        except requests.exceptions.Timeout:
#             print('ip问题,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        except requests.exceptions.ConnectionError:
#             print('ip被封,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        else:
            index+=1
            if collection.find_one({'BasicInfo': doctor_info['BasicInfo'],'Hospital': doctor_info['Hospital']}):
                pass
#                 print(str(index)+'重复',end = ',')
            else:
                result = collection.insert_one(doctor_info)
#                 print(index,end = ',')

def get_doctorinfo_pushin_mangoDB7(x):
    index = 0
    shenjing_2_flag = 0
    while index<len(doctor_url_notchongfu7):
        proxy = random.choice(proxy_list)# 随机从ip池中选出一个ip
        try:
            doctor_info = get_one_doctor_info(doctor_url_notchongfu7[index], proxy)
            time.sleep(0.1)
        except IndexError:
#             print('ip用完了',index,end = ',')
            break
        except AttributeError:
#             print('神经了2',end = ',')
            shenjing_2_flag+=1
            if shenjing_2_flag>3:
                shenjing_2_flag = 0
                index+=1
        except ConnectionError:
            pass
#             print('连接错误',end = ',')
        except requests.exceptions.Timeout:
#             print('ip问题,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        except requests.exceptions.ConnectionError:
#             print('ip被封,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        else:
            index+=1
            if collection.find_one({'BasicInfo': doctor_info['BasicInfo'],'Hospital': doctor_info['Hospital']}):
                pass
#                 print(str(index)+'重复',end = ',')
            else:
                result = collection.insert_one(doctor_info)
#                 print(index,end = ',')

def get_doctorinfo_pushin_mangoDB8(x):
    index = 0
    shenjing_2_flag = 0
    while index<len(doctor_url_notchongfu8):
        proxy = random.choice(proxy_list)# 随机从ip池中选出一个ip
        try:
            doctor_info = get_one_doctor_info(doctor_url_notchongfu8[index], proxy)
            time.sleep(0.1)
        except IndexError:
#             print('ip用完了',index,end = ',')
            break
        except AttributeError:
#             print('神经了2',end = ',')
            shenjing_2_flag+=1
            if shenjing_2_flag>3:
                shenjing_2_flag = 0
                index+=1
        except ConnectionError:
            pass
#             print('连接错误',end = ',')
        except requests.exceptions.Timeout:
#             print('ip问题,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        except requests.exceptions.ConnectionError:
#             print('ip被封,删之',end = ',')
            if proxy in proxy_list:
                proxy_list.remove(proxy)
        else:
            index+=1
            if collection.find_one({'BasicInfo': doctor_info['BasicInfo'],'Hospital': doctor_info['Hospital']}):
                pass
#                 print(str(index)+'重复',end = ',')
            else:
                result = collection.insert_one(doctor_info)
#                 print(index,end = ',')


def get_proxy_list(file_path = '/Users/litianhao/Desktop/ip池/ip.txt'):
	'''
	:param file_path: 代理ip的txt文件
	:return: 代理ip的列表
	'''
	proxy_list = []
	with codecs.open(file_path, 'r', 'utf8')as f:
		for ip in f:
			proxy_list.append(ip.strip())
	return  proxy_list
#%%
if __name__ == '__main__':
	#%%
	######连接数据库
	ua = UserAgent()
	client = pymongo.MongoClient(host = 'localhost', port = 27017)
	db = client.admin
	db.authenticate('litianhao', '19960812')
	mydb = client["spider_info_haodafu"]
	collection = mydb.doctor
	#%%
	######得到所有医生url的生成器
	department_url = get_department_url()
	all_doctorpage_all_department_url = get_allDoctorPage_url_of_departmentList(department_url)
	all_doctor_url = []
	for all_dpage_url in all_doctorpage_all_department_url:
		all_doctor_url.append(get_all_doctor_url_from_all_pages_one_department(all_dpage_url))
	######将所有医生的url分科室存在不同txt文件中
	#%%
	for i in tqdm(range(0, len(all_doctor_url))):
		department_alldoctor_url = [x for x in all_doctor_url[i]]
		department_alldoctor_url = set(department_alldoctor_url[0])
		with codecs.open('/Users/litianhao/Desktop/所有医生url/' + str(i) + '.txt', 'w', 'utf8')as w:
			for x in department_alldoctor_url:
				w.write(x + '\n')
	#%%
	######
	for i in range(1,140):
		proxy_list = get_proxy_list()
		one_department_alldcotorurl = []
		with codecs.open('/Users/litianhao/Desktop/所有医生url/'+str(i)+'.txt','r', 'utf8')as f:
			for url in f:
				one_department_alldcotorurl.append(url.strip())
		n = (len(one_department_alldcotorurl)//8)+1
		inputs = [one_department_alldcotorurl[i:i + n] for i in range(0, len(one_department_alldcotorurl), n)]
		doctor_url_notchongfu1, doctor_url_notchongfu2, doctor_url_notchongfu3, \
		doctor_url_notchongfu4, doctor_url_notchongfu5, doctor_url_notchongfu6, \
		doctor_url_notchongfu7, doctor_url_notchongfu8 = inputs
		# start = time.time()
		# with Pool(8) as pool:
		# 	pool.map(get_doctorinfo_pushin_mangoDB, inputs)
		# end = time.time()
		# print(end - start)
		# start = time.time()
		pool = Pool(processes = 8)
		pool.apply_async(get_doctorinfo_pushin_mangoDB1, (1,))
		pool.apply_async(get_doctorinfo_pushin_mangoDB2, (2,))
		pool.apply_async(get_doctorinfo_pushin_mangoDB3, (3,))
		pool.apply_async(get_doctorinfo_pushin_mangoDB4, (4,))
		pool.apply_async(get_doctorinfo_pushin_mangoDB5, (5,))
		pool.apply_async(get_doctorinfo_pushin_mangoDB6, (6,))
		pool.apply_async(get_doctorinfo_pushin_mangoDB7, (7,))
		pool.apply_async(get_doctorinfo_pushin_mangoDB8, (8,))
		pool.close()
		pool.join()
		# end = time.time()
		# print(end - start)
		#维护更新代理池
		with codecs.open('/Users/litianhao/Desktop/ip池/ip.txt', 'w', 'utf8')as f:
			for ip in proxy_list:
				f.write(ip + '\n')
	######查询表中所有信息
	#%%
	for x in collection.find():
		print(x)

