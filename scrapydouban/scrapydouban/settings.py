# -*- coding: utf-8 -*-

# Scrapy settings for scrapydouban project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'scrapydouban'

SPIDER_MODULES = ['scrapydouban.spiders']
NEWSPIDER_MODULE = 'scrapydouban.spiders'

ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = 3

DOWNLOADER_MIDDLEWARES = {
    'scrapydouban.middlewares.UserAgentMiddleware':401,
    'scrapydouban.middlewares.Cookies_Proxy_Middleware':402,
     
} 
#USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'

