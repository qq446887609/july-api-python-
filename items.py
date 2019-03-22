# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LiuliItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()       #标题
    url =  scrapy.Field()        #文章地址
    description = scrapy.Field() #描述
    cover_url = scrapy.Field()   #封面图片url
    content = scrapy.Field()     #文章详情
    tag = scrapy.Field()         #文章关键字 , 号分割 便于查找
    created_at = scrapy.Field()  #创建时间
