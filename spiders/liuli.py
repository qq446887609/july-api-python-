# -*- coding: utf-8 -*-
import scrapy
from pc.items import LiuliItem
from pyquery import PyQuery as pq
from pc.lib.Db import Db


class LiuliSpider(scrapy.Spider):

    name = 'liuli' #爬虫名称
    allowed_domains = ["llss.news/wp/"] #此域名下的爬取全部跳出
    start_urls = ['http://llss.news/wp/category/all/anime/']  #开始爬取开始页
    old_url = '' #上一页url(避免无法结束爬虫)
    repeat = 0 #验证是否重复爬取
    
    def parse(self, response):
        content = response.css('.custom-background').extract()[0]   #获得css方法首先获得body内全部内容
        doc = pq(content) #转换为pyquery 解析库
        articles = doc('article').items() #获得所有article div
        for article in articles:
            item = LiuliItem()
            item['title'] = article.find('.entry-title a').text()   #获得titlte  后期 百度翻译api 翻译标题
            item['url'] = article.find('.entry-title a').attr('href') #获得url

            #检测记录是否存在 如果存在 说明都已经抓取 后面的都不再抓取  
            if self.check_article_exits(item['url']) == True:
                self.repeat = 1
                print(item['title']+'此记录后的已经爬取过')
                break

            if item['url'] and item['title']:
                item['content'] = self.crawl_detail(item['url']) #前往爬取详情

            article.find('.entry-content p a').remove()
            item['description'] = article.find('.entry-content p:last').text()
            item['cover_url'] = article.find('.entry-content p img').attr('src')
            article.find('.entry-utility-prep-tag-links').remove()
            item['tag'] = article.find('.tag-links').text()
            yield item

        next = doc('.page.larger:first')  #获得下一页爬取地址
        url = response.urljoin(next.attr('href')) #生成请求

        #链接不为空接着爬取下一页
        if url is not None and url != self.old_url and self.repeat!= 1:
            self.old_url = url 
            yield scrapy.Request(url = url,callback=self.parse,dont_filter=True)

    #爬取文章详情
    def crawl_detail(self,url):
        doc = pq(url)
        content = doc('.entry-content')
        
        if content is None:
            return ''
        return str(content)

    #查询单条记录
    def check_article_exits(self,url):
        table = 'articles'
        db = Db()
        result = db.find(table = table,params = {"where":" url = '"+url +"'",'field':True})
        if result is not None:
            return True
        return False


