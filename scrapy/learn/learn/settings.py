# -*- coding: utf-8 -*-
import os
# Scrapy settings for learn project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'learn'

SPIDER_MODULES = ['learn.spiders']
NEWSPIDER_MODULE = 'learn.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'learn (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 100

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'learn.middlewares.LearnSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'learn.middlewares.LearnDownloaderMiddleware': 543,
   'learn.middlewares.RandomUserAgentMiddleware':543,
   'learn.middlewares.MyRetryMiddleware':302,

}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   # 'learn.pipelines.LearnPipeline': 300,
   'learn.pipelines.MongoPipeline':1,
   'learn.pipelines.MongoPipeline1':2,
	# 'scrapy.pipelines.images.ImagesPipeline': 1,
}

#IMAGES_URLS_FIELD = "图片url的item字段"
project_dir = os.path.abspath(os.path.dirname(__file__))

#IMAGES_STORE = os.path.join(project_dir,'images')

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

#mongo数据库设置
#好大夫
# MONGO_URI = 'localhost'
# MONGO_DB = "spider_info_haodafu"
# MONGO_COL = "doctor_plus"
#药智网
MONGO_URI = 'localhost'
MONGO_DB = "spider_info_yaozhi"
MONGO_COL = "hospital"
MONGO_COL_CLN = "clinic"


#ip代理和用户代理设置
ProxyUser = "HBG6Q6L1F9V7S17D"
ProxyPass = "DC4FE92F76E95AE6"
RANDOM_UA_TYPE = "chrome"

#错误重试
RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 503, 504, 400, 408, 403, 429]
RETRY_PRIORITY_ADJUST = -1

#日志设定
LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
LOG_FILE = 'log/mySpider.log'
LOG_LEVEL = 'WARNING'