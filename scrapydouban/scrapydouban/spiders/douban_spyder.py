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