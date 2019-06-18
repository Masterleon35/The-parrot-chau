from scrapy.cmdline import execute
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy","crawl","haodafu"])
# execute(["scrapy","crawl","jobbole"])
execute(["scrapy","crawl","yaozhi"])