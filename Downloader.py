import random
import requests
import json
class Downloader():
 
    invalid_ip_count=0
    ip_list_local=[]

    # 随机获取一个UserAgent
    @staticmethod
    def getUserAgent():
        UA_list = [
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) App leWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53",
            "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13",
            "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ;  QIHU 360EE)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; Maxthon/3.0)",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Mozilla/5.0 (Macintosh; U; IntelMac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1Safari/534.50",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]
        return random.choice(UA_list)



    # 随机获取一个Cookie，使用前先通过浏览器等方式先获取cookie
    @staticmethod
    def getCookie():
        cookie_list = [
            'cy=8; cye=chengdu; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; _lxsdk_cuid=166811ebad2c0-0d52a407e0bb01-b79193d-144000-166811ebad3c8; _lxsdk=166811ebad2c0-0d52a407e0bb01-b79193d-144000-166811ebad3c8; _hc.v=4fe55c5f-3a76-1af1-22a9-577c06d41cce.1539764567; s_ViewType=10; _lxsdk_s=16681792a0c-e24-ee0-1c7%7C%7C161',
            ]
        cookie = random.choice(cookie_list)
        return cookie

    #使用付费IP代理池 讯代理 获得IP
    @staticmethod
    def get_ip_list():
        url=''
        try:
            json_data=requests.get(url).json()
            ips=json_data['RESULT']
            proxies=[]
            for data in ips:
                proxies.append('http://'+str(data['ip'])+':'+str(data['port']))
            print('got ip proxies: ',len(proxies))
        except:
            proxies=[]
        return proxies

    def get_random_ip(self,ip_list):
        proxy_ip = random.choice(ip_list)
        proxies = {'http': proxy_ip}
        return proxies


    def getProxy(self):
        global invalid_ip_count
        global ip_list_local
        print('\n invalid ip count:',invalid_ip_count)
        if len(ip_list_local)<1 or float(invalid_ip_count/len(ip_list_local))>0.5:
            invalid_ip_count=0
            ip_list_local=Downloader.get_ip_list()
        proxy=get_random_ip(ip_list_local)
        print('using proxy:',proxy)
        return proxy

    # 使用requests获取HTML页面
    def getHTML(self,url,user_agent=True,ip_proxy=False,cookie=False):
        global invalid_ip_count
        global ip_list_local
        User_agent=Downloader.getUserAgent() if user_agent else None
        cookie= Downloader.getCookie() if cookie else None
        headers = {
            'User-Agent': User_agent,
            'Cookie':cookie,
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        }

        try:
            web_data=requests.get(url,headers=headers,proxies=getProxy(self) if ip_proxy else None,timeout=20)#超时时间为20秒
            status_code=web_data.status_code
            retry_count=0
            while(str(status_code)!='200' and retry_count<5):
                print('status code: ',status_code,' retry downloading url: ',url , ' ...')
                invalid_ip_count+=1
                web_data=requests.get(url,headers=headers,proxies=getProxy(self) if ip_proxy else None,timeout=20)
                status_code=web_data.status_code
                retry_count+=1
            if str(status_code)=='200':
                return web_data.content.decode('utf-8')
            else:
                return "ERROR"
        except Exception as e:
            print(e)
            return "ERROR"
