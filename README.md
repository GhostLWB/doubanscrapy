# 豆瓣电影影评爬取详细教程

## 在爬取之前，你得确保你已经有以下的条件：
>python3 环境 （在我的机子上是python 3.6.5）
>scrapy 已经安装
>有一个Python的IDE 我这里是Spyder

为了方便调试，在这里我们先在Windows10系统进行编码，然后在阿里云服务器上运行

## 需求分析
在这里呢我们要爬取某个特定电影的评论信息，包括：
    1. 这个电影的整体评分，实时评分人数，各个星段的评价分布。由于这个评分是动态更新的，所以我们不是爬一次就完事了，要按照一定的时间间隔去爬取更新
    ![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/16775380.jpg)
    2. 这个电影的观众评论内容，评论观众的昵称，ID，评论日期，该评论的“有用”数
    ![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/38344190.jpg)

需求不多，我们先来看一下该怎么爬
## 熟悉scrapy
scrapy的架构如下：
![](http://oz9fdm91f.bkt.clouddn.com/18-4-13/84645295.jpg)
工欲善其事，必先利其器。在这里我们的有力工具就是scrapy，它是一个高级Python爬虫框架，将爬虫的流程模块化，让你专心于爬虫逻辑的处理，请求调度和文件保存的事情它帮你包了。
scrapy的官方文档写的很良心，对scrapy的学习建议从官方文档下手
[scrapy 官方文档传送门](https://docs.scrapy.org/en/latest/)

不过在这个项目里你没必要从头到尾把官方文档看一遍，我会挑需要的展示在这里，等你做完这个项目对scrapy产生了兴趣，再花一天时间仔细看下吧。

### 首先我们来建一个scrapy项目
看看官网是怎么说的
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/79848086.jpg)
我们先新建一个文件夹，我建在了桌面上（F:\\Desktop\scrapydouban\），这个地方就会是你打算放置scrapy代码的目录，然后按住shift+右键在当前目录打开cmd窗口，我这里是默认用的powershell,这并不影响。在命令行输入
```
scrapy startproject scrapydouban
```
来新建一个工程，相关的文件scrapy会给你生成好。
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/78294036.jpg)如果你打算在别的目录建工程，在你的项目名称后面加上路径就好
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/43237733.jpg)
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/95770808.jpg)

建立好的scrapy工程结构会是这个样子的 
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/54126528.jpg)
下面来分析一下每个文件的作用：
>    scrapy.cfg 这是scrapy的配置文件，里面配置了这个项目的设置和项目的名称，使用它默认的就好
    \_\_init\_\_.py 这个是使得这个文件夹的内容成为模块必须的文件，保留默认的就好
    items.py 这个文件用来定义你爬回来的东西怎样保存
    middlewares.py 这个是中间件，定义了在请求发送之前可以做的处理（加cookie加useragent等），以及获得响应之后的预处理（状态判断、重定向等等）
    pipelines.py 这个文件定义如何处理爬回来已经存放在items里面的数据
    setting.py 不须多说，这个文件里定义了对项目的各种设置（采用哪个middware,设置爬取时间间隔等等）
    spiders/ 
        \_\_init\_\_.py 跟外面文件夹下的是一样的作用，留着不用改

创建完项目框架之后，我们来开始爬数据
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/21698683.jpg)

## 豆瓣网址链接分析

我们以4月初上映的高分电影《头号玩家》为例，
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/23544588.jpg)
我们要爬的网站是这个 [头号玩家 短评](https://movie.douban.com/subject/4920389/comments?status=P)

我们往下拉到最后，点击后页，跳转之后查看浏览器的URL，发现变成了这个链接 
```
https://movie.douban.com/subject/4920389/comments?start=20&limit=20&sort=new_score&status=P&percent_type=
```
其中，
1. https://movie.douban.com/是主机名（host）
2. subject/4920389/表示是头号玩家这个电影的资料
3. start=20表示当前页面是从第二十条评论开始加载
4. sort=new_score表示按照热门程度排序
5. limit 应该是每页加载的最多评论数
6. status=P表示这是已经看过的人的评论，如果status=F则是想看的人的评论
7. percent_type= 空表示全部评论 percent_type=h表示只看好评 percent_type=m表示只看中评，percent_type=l表示只看差评

那我们要爬的时候，其实只要把URL中的start每次加20就可以了，又或者，根据返回的页面，查看它的“下页”对应的网页元素，从中提取下一页的URL，再yield出去

## 开始写代码
我们得在项目的spiders文件夹中新建一个python文件，名称为douban_spyder.py，这个文件是爬虫的主文件，必须继承scrapy.Spider这个类
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/1408624.jpg)
在我们的douban_spyder.py中，必须实现三个东西：name属性、start_requests()方法和parse()方法
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/98098905.jpg)
其中，
1. name是定义这个爬虫的名字
2. start_requests()方法是构造将要爬的网页URL，一般采用yield方式返回每个URL，它们将交给scrapy框架去调度。
3. parse() 这个方法定义了返回响应之后如何解析，这个是scrapy默认的回调函数，如果你想分别对不同的URL进行解析，那么定义自己的回调函数也是可以的，只需要在start_requests()里构造request的时候加入callback=<你的回调函数>就可以了


我们在start_requests()中构造这个Request，返回给自己定义的回调函数
```
import scrapy

class douban_spyder(scrapy.Spider):
    name='douban_spyder'
    def start_requests(self):
        start_url='https://movie.douban.com/subject/4920389/comments?start=20&limit=20&sort=new_score&status=P&percent_type='
        return scrapy.Request(url=start_url,callback=self.dbSrearch)
 
```

## 解析网页代码
接下来对爬回来的网页进行解析，我们得先看一下原始的爬下来的网页源代码是什么样子的，好好分析一番，然后在制定解析策略。
我的方法是自己写一个爬虫，作用就是把这个网页的响应保存在TXT文件中，有的人可能会问，为什么不用浏览器右键的“查看源代码”呢，因为你在浏览器看得见的是浏览器渲染后给你的，有的内容是浏览器从js中取出来数据渲染上去的，这些额外的数据可能不在你所获得的响应里面，有时候，网页还会涉及到一个请求转发和请求重定向的过程，请求转发不需要我们处理，因为这是个服务器行为，请求重定向则需要我们处理，这是个客户端行为，相当于客户端发送了两次请求，浏览器中的URL会发生改变，比如网站登录后的页面跳转行为等等。
这个爬虫太简单了，直接给代码了，单独建一个python文件运行就好：

```
import requests
url ='https://movie.douban.com/subject/4920389/comments?start=20&limit=20&sort=new_score&status=P&percent_type='
html = requests.get(url).text
with open('.\sourcehtml.txt','w') as f:
    f.write(html)

```
可以看到返回的源代码内容：

![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/50539293.jpg)
再看看从浏览器中右键查看的源代码，在这里其实是和我们保存在文件中的是一致的 = = 
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/8078657.jpg)
好嘛，直接在浏览器中右键看源代码就好了
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/8708944.jpg)

看了一下这页面结构，解析起来难度不高
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/12418611.jpg)
scrapy 自带lxml解析，官网有写到
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/24374733.jpg)
它被封装在Selector类中，使用的时候需要导入，代码是
```
from scrapy.selector import Selector
```

每个评论放在一个class为"comment"的div容器里，首先根据这个要素把每个div提取出来，再在这个div里分析每个元素所在的位置，xpath代码都十分简单，这里就不解释了，要看xpath语法，这里有一篇很不错的教程：[python中使用XPath](https://www.cnblogs.com/gaochsh/p/6757475.html)
由于电影的评分只有一个页面，我就不定义在item里面了，直接写在了文件里，看代码即可
下面是整个douban_spyder.py的内容：
```
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 19:56:04 2018

@author: Li-We
"""

import scrapy
from scrapy.selector import Selector
from scrapydouban.items import DBScrapyItem
from scrapy.http import Request
import re

class douban_spyder(scrapy.Spider):
    name='douban_spyder'
    
    def start_requests(self):
        start_url='https://movie.douban.com/subject/4920389/comments?start=20&limit=20&sort=new_score&status=P&percent_type='
        yield scrapy.Request(url=start_url,callback=self.dbSearch)#必须要用yield而不能用return
        moviedetail_url = 'https://movie.douban.com/subject/4920389/?from=showing'
        yield scrapy.Request(url = moviedetail_url,callback = self.dbMoviedetail)
        
    def dbSearch(self,response):
        scrapydoubanItem=DBScrapyItem()
        selector = Selector(response)
        divs = selector.xpath('//div[@class="comment"]')
        for div in divs:
            scrapydoubanItem['useful_count'] = div.xpath('//span[@class="comment-vote"]/span[@class="votes"]/text()').extract()
            scrapydoubanItem['username'] = div.xpath('//span[@class ="comment-info"]/a/text()').extract()
            scrapydoubanItem['userlink'] = div.xpath('//span[@class ="comment-info"]/a/@href').extract()
            scrapydoubanItem['comment_time'] = div.xpath('//span[@class ="comment-info"]/span[@class="comment-time "]/@title').extract()
            scrapydoubanItem['comment'] = div.xpath('//p[@class=""]//text()').extract()
            yield scrapydoubanItem#请记得每次都要yeild这个item出去，否则你会发现没有数据没有保存
        #查找下一页
        nextpage_urls = selector.xpath('//div[@id="paginator"]/a[@class="next"]/@href').extract()
        for nextpage in nextpage_urls:
            yield Request(url = 'https://movie.douban.com/subject/4920389/comments'+nextpage,callback = self.dbSearch)#将下一页的URL发送到scrapy待爬队列
    
    def dbMoviedetail(self,response):
        selector = Selector(response)
        with open('.\moviedetail.txt','w')as f:
            title = selector.xpath('//span[@property="v:itemreviewed"]//text()').extract()
            score = selector.xpath('//div[@class="rating_self clearfix"]/strong/text()').extract()
            vote_count=selector.xpath('//div[@class="rating_self clearfix"]//a[@class="rating_people"]//text()').extract()
            rating_weights=selector.xpath('//div[@class="ratings-on-weight"]/div[@class="item"]')
            f.write("电影名称:"+title[0]+'\n'+"电影评分:"+score[0]+'\n'+"评分人数:"+vote_count[0]+'\n')            
            rate_title = rating_weights[0].xpath('//span[starts-with(@class,"stars")]/text()').extract()
            rate_per = rating_weights[0].xpath('//span[@class="rating_per"]/text()').extract()
            rate_titles=[]
            for rate in rate_title:
                rate = re.findall('(\d)星',rate)[0]
                rate_titles.append(rate+'星')
            for i in range(0,5):
                f.write(rate_titles[i] +':'+rate_per[i]+'\n')
            betterthan = ' '.join(selector.xpath('//div[@class="rating_betterthan"]//text()').extract())
            f.write(betterthan)
```
接下来我们要定义Item，在这里我自己定义了一个类，用来保存爬取到的Item，它采用的是类似字典的结构，左边的变量名便是你在爬虫代码中的scrapydoubanItem['变量名']
items.py

```
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapydoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
class DBScrapyItem(scrapy.Item):
    username = scrapy.Field()
    userlink = scrapy.Field()
    comment_time = scrapy.Field()
    useful_count = scrapy.Field()
    comment = scrapy.Field()
    

    
```

## 使得爬虫更加健壮[设置中间件]
由于现在爬虫越来越多，爬虫开发者的水平参差不齐，有的人写出来的爬虫简直是病毒，不停向服务器发送请求，造成阻塞，又不懂得设置一下时间间隔，使得服务器不堪重负。于是比较牛皮的网站都有了自己的反爬虫策略，并且还在不断升级。
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/48364884.jpg)
一般来说，网站反爬虫有以下的策略：
1. 同ip请求过于频繁，封ip
2. 同账号请求过于频繁，封账号
3. 将页面内容封装在js代码里面异步加载
4. 需要预登录，跳转两次
或者有别的，我没有太多了解过，以上是我踩过的坑

爬虫采取的反击有以下：
1. 在请求的头部加入user-agent伪装成浏览器
2. 在请求头部加入cookie对付需要登录才能看的网站
3. 在请求头部加入IP代理

所以我们现在要伪装一下我们的爬虫，在middware里面对request进行包装
中间件是scrapy在处理请求和响应之前和之后调用的
第一步，加user-agent，加上这个可以让你的爬虫伪装成浏览器，网上有人搜集了最全的agents，在这里
```
agents = [
    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
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
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b4pre) Gecko/20100815 Minefield/4.0b4pre",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0 )",
    "Mozilla/4.0 (compatible; MSIE 5.5; Windows 98; Win 9x 4.90)",
    "Mozilla/5.0 (Windows; U; Windows XP) Gecko MultiZilla/1.6.1.0a",
    "Mozilla/2.02E (Win95; U)",
    "Mozilla/3.01Gold (Win95; I)",
    "Mozilla/4.8 [en] (Windows NT 5.1; U)",
    "Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)",
    "HTC_Dream Mozilla/5.0 (Linux; U; Android 1.5; en-ca; Build/CUPCAKE) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.2; U; de-DE) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/234.40.1 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-us; sdk Build/CUPCAKE) AppleWebkit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.1; en-us; Nexus One Build/ERD62) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-us; htc_bahamas Build/CRB17) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.1-update1; de-de; HTC Desire 1.19.161.5 Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Sprint APA9292KT Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 1.5; de-ch; HTC Hero Build/CUPCAKE) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; ADR6300 Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.1; en-us; HTC Legend Build/cupcake) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 1.5; de-de; HTC Magic Build/PLAT-RC33) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1 FirePHP/0.3",
    "Mozilla/5.0 (Linux; U; Android 1.6; en-us; HTC_TATTOO_A3288 Build/DRC79) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 1.0; en-us; dream) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-us; T-Mobile G1 Build/CRB43) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari 525.20.1",
    "Mozilla/5.0 (Linux; U; Android 1.5; en-gb; T-Mobile_G2_Touch Build/CUPCAKE) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 2.0; en-us; Droid Build/ESD20) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Droid Build/FRG22D) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.0; en-us; Milestone Build/ SHOLS_U2_01.03.1) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.0.1; de-de; Milestone Build/SHOLS_U2_01.14.0) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 0.5; en-us) AppleWebKit/522  (KHTML, like Gecko) Safari/419.3",
    "Mozilla/5.0 (Linux; U; Android 1.1; en-gb; dream) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 2.0; en-us; Droid Build/ESD20) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.1; en-us; Nexus One Build/ERD62) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Sprint APA9292KT Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; ADR6300 Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-ca; GT-P1000M Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 3.0.1; fr-fr; A500 Build/HRI66) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/525.10  (KHTML, like Gecko) Version/3.0.4 Mobile Safari/523.12.2",
    "Mozilla/5.0 (Linux; U; Android 1.6; es-es; SonyEricssonX10i Build/R1FA016) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
    "Mozilla/5.0 (Linux; U; Android 1.6; en-us; SonyEricssonX10i Build/R1AA056) AppleWebKit/528.5  (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
]
```

每次随机选一个加在request的头部就好了
第二步，加上cookie模拟登录
比如在豆瓣，你登录以后，在浏览器页面右键-检查元素，然后我做了张图，希望你们能看得懂
![](http://oz9fdm91f.bkt.clouddn.com/18-4-12/70117794.jpg)



第三步，加上IP代理
我使用的是这个博主提供的IP代理池
[构建爬虫代理池](http://blog.nghuyong.top/2017/10/19/spider/%E6%9E%84%E5%BB%BA%E7%88%AC%E8%99%AB%E4%BB%A3%E7%90%86%E6%B1%A0/)
然后每次都获取可用的IP代理

那在middleware里面要怎么写呢，我写这个教程的时候自己写了一遍，在scrapy自动生成的代码上进行，但是写出来的Middleware总是没有调用，本来代码一个小时就写完了，硬是debug到了第二天中午，很头大，所以我参考了网上一种写法，暂且这样吧
写法是这样的：
先把scrapy自动生成的middlewares.py中所有的方法和类都删掉，我们自己写两个个类：UserAgentMiddleware 和 Cookies_Proxy_Middleware，分别进行user-agent和cookie、proxy的配置
middlewares.py
```
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

   
```


## 配置工程
在setting中配置工程的各种参数
settings.py
```
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


```
我这里就简单设置了一下并行度，爬取延迟和中间件

一共四个文件需要编辑：
![](http://oz9fdm91f.bkt.clouddn.com/18-4-13/24144964.jpg)
## 运行
用命令行执行scrapy项目，想要将结果保存成CSV文件，需要加上几个参数
-o 文件名 -t 文件类型

在含有scrapy.cfg的文件夹打开命令行，执行：
```
scrapy crawl douban_spyder -o douban.csv -t csv

```
需要注意的是这里的项目名称，得是你在爬虫文件中定义的name属性中的值
## 结果
执行上面的运行命令可以获得.csv形式保存的文件
![](http://oz9fdm91f.bkt.clouddn.com/18-4-13/70845187.jpg)
打开看内容的时候如果是乱码，就用记事本打开，然后另存，选择编码为UTF-8就好了
![](http://oz9fdm91f.bkt.clouddn.com/18-4-13/73289932.jpg)
覆盖原来的文件，再次打开就是正常显示了
![](http://oz9fdm91f.bkt.clouddn.com/18-4-13/14753342.jpg)

电影评分：
![](http://oz9fdm91f.bkt.clouddn.com/18-4-13/8585844.jpg)

## 在云服务器上定时运行
好了，做到这里你其实已经完成了一个可以用的爬虫，但是我们之前说，因为影评是动态更新的，每次爬取的数据只代表直到目前的数据，如果要获取最新的数据，当然是要定时爬取，这我用的是阿里云服务器，使用crontab定时任务，如果你没有，跳过这一步即可，手动在本地执行scrapy crawl也没有问题
使用xshell连接服务器，切换到/usr/apps目录，我们把爬虫放在这里
![](http://oz9fdm91f.bkt.clouddn.com/18-4-13/66152607.jpg)
打开xftp，上传爬虫工程文件
![](http://oz9fdm91f.bkt.clouddn.com/18-4-13/65308685.jpg)
设置crontab命令
```
0 */5 * * * cd /usr/apps/scrapydouban && /usr/apps/python3/bin/scrapy crawl douban_spyder -o douban.csv -t csv

```
![](http://oz9fdm91f.bkt.clouddn.com/18-4-13/31826159.jpg)
使用crontab -l命令查看已经存在的定时任务
![](http://oz9fdm91f.bkt.clouddn.com/18-4-13/29550398.jpg)
表示每5个小时爬取一次
完成！
## 遇到的错误
报错：
TypeError: 'Request' object is not iterable

解决：在start_request()方法中将Request返回要用yield 而不是return

报错:
twisted.web._newclient.ResponseNeverReceived: [<twisted.python.failure.Failure OpenSSL.SSL.Error: [('SSL routines', 'SSL23_GET_SERVER_HELLO', 'unknown protocol')]>]

再次启动就解决了，我也不知道为什么突然又不报这个错了

报错：http状态码 403
访问被拒绝，被识别出来了,换IP或者换cookie
