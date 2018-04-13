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
    
