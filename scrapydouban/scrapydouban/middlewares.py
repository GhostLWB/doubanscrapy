# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random
import requests
import json
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class UserAgentMiddleware(object):
    """ 换User-Agent """
    def process_request(self, request, spider):
         agents=["Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
                "Avant Browser/1.2.789rel1 (http://www.avantbrowser.com)",
                "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5",
                "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9",
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
                "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14",
                "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14",
                "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1",
                "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7",
                "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.10) Gecko/2009042316 Firefox/3.0.10",
                "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-GB; rv:1.9.0.11) Gecko/2009060215 Firefox/3.0.11 (.NET CLR 3.5.30729)",
                "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6 GTB5",
                "Mozilla/5.0 (Windows; U; Windows NT 5.1; tr; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 ( .NET CLR 3.5.30729; .NET4.0E)",
                "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
                "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110622 Firefox/6.0a2",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre",]
         
         agent = random.choice(agents)
         request.headers["User-Agent"] = agent
'''
class ProxyMiddleware(object):


    def process_request(self,request,spider):
        """ 为爬虫加上代理IP，避免IP被封"""
        proxyres = requests.get('http://proxy.nghuyong.top').text
        totalproxies = json.loads(proxyres)['num']
        if (totalproxies>0):
            proxylist=json.loads(proxyres)['data']
            proxy = random.choice(proxylist)
            request.meta['proxy'] ="http://"+proxy['ip_and_port']
'''        
class Cookies_Proxy_Middleware(RetryMiddleware):
    """ 维护Cookie 和代理IP"""

    def __init__(self, settings, crawler):
        RetryMiddleware.__init__(self, settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def process_request(self, request, spider):
        """ 为爬虫加上cookie，模拟登录 """
        mycookie = 'bid=baf3NkFR5Dw; ll="118318"; __yadk_uid=zInDRd9Ba91W4YuGziZo9EZeYGVhd7JM; _vwo_uuid_v2=DEC30022151DB337E1E8FF98E02FED6FC|9a2c17301585d5e122f36ea34f221915; ps=y; dbcl2="49365204:/uGP1KFj2OQ"; push_noty_num=0; push_doumail_num=0; ap=1; ct=y; ck=PlrQ; __utma=30149280.726786722.1523515595.1523541171.1523584454.5; __utmb=30149280.0.10.1523584454; __utmc=30149280; __utmz=30149280.1523584454.5.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=223695111.831534826.1523515595.1523541171.1523584454.5; __utmb=223695111.0.10.1523584454; __utmc=223695111; __utmz=223695111.1523584454.5.3.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1523584454%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DDX3aohVNEDo9VRyanhNVMhLr3Fyl2d-zikQ7hkBuM5ylk9fgbaVDNujfkF_NP4zX%26wd%3D%26eqid%3Db19a01750005a3ea000000035ad00db9%22%5D; _pk_id.100001.4cf6=0f80708a5e76f07c.1523515595.5.1523584454.1523540930.; _pk_ses.100001.4cf6=*'
        request.cookies=self.builddict(mycookie)
        
    ''' 因为request接受的cookie是字典形式，所以要把从浏览器赋值过来的cookie解析成字典形式 '''
    def builddict(self,string):
        cookiedic ={} 
        dictstr='{'
        linelist = string.split(';')
        for line in linelist:
            key = line.split('=')[0]
            value = line.split('=')[1]
            dictstr = dictstr+'"'+key+'"'+':'+"'"+value+"'"+','
            cookiedic[key]=value
        dictstr= dictstr.rstrip(',')
        dictstr= dictstr+'}'
        #print(dictstr)
        return cookiedic
    def process_response(self, request, response, spider):
        if response.status in [403, 414]:
            reason = response_status_message(response.status)
            print('change ip proxy and retrying...')
            proxyres = requests.get('http://proxy.nghuyong.top').text
            totalproxies = json.loads(proxyres)['num']
            if (totalproxies>0):
                proxylist=json.loads(proxyres)['data']
                proxy = random.choice(proxylist)
                request.meta['proxy'] ="http://"+proxy['ip_and_port']
                return self._retry(request,reason,spider)
            #print("%s! Stopping..." % response.status)
            #os.system("pause")
        else:
            return response

   