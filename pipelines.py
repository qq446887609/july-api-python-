from scrapy.exceptions import DropItem
import pymysql
from twisted.enterprise import adbapi #异步执行mysql方法
import time
from pc.lib.Fanyi import Youdao
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

class mysqlDb(object):

    DB_PREFIX = 'july_'

    #初始化数据库链接
    def __init__(self, ):
        dbparms = dict(
            host='localhost',
            db='july',
            user='root',
            passwd='root',
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor, # 指定 curosr 类型
            use_unicode=True,
        )
        # 指定参数做数据库的模块名和数据库参数参数
        self.dbpool = adbapi.ConnectionPool("pymysql", **dbparms)



    # pipeline
    def process_item(self, item, spider):

        print('6666666666')
        print(item)
        print('6666666666')

        #验证
        ck_status,ck_msg = self.checkItem(item,spider.name)
        print(ck_msg)
        if ck_status == False:
            return DropItem(ck_msg)

        #洗数据
        item = self.buildItem(item,spider.name)

        id = self.dbpool.runInteraction(self.do_insert, item,spider.name) # #使用twisted将mysql插入变成异步执行
        print(id)



    #插入
    def do_insert(self, cursor, item,spider):

        table = self.get_table(spider)
        keys = ",".join(item.keys()) #添加数据key
        values = ",".join(["%s"]* len(item)) #重复多个%s占位符

        sql = 'insert ignore into '+self.DB_PREFIX+'{table}({keys}) values({values})'.format(table=table,keys=keys,values=values)

        try:
            cursor.execute(sql,tuple(item.values()))
            id = cursor.lastrowid #获得添加自增id
            #self.dbpool.commit()  adbapi.ConnectionPool 会自动调用commit
            return id
        except pymysql.err.ProgrammingError as err:
            print(err)
            #self.dbpool.rollback()

        self.dbpool.close()
  

    # 获得表名
    def get_table(self,spider):

        table = ''
        if spider == 'liuli':
            table = 'articles'
        
        return table



    #查询单条记录
    def do_query_one(self,cursor,sql):
        
        try:
            cursor.execute(sql)
            row = cursor.fethone() #获得单条数据
        except pymysql.err.ProgrammingError as err:
            print(err)

        if row is None:
            return False
        return row


    
    #验证item
    def checkItem(self,item,spider):
        
        #验证liuli 爬虫
        if spider == 'liuli':
            if item['url'] is None or item['url'] == '':
                return False,'url is missing'
            if item['title'] is None or item['title'] == '':
                return False,'title is missing'
            
            # exist = self.dbpool.runInteraction(self.checkLiuliExist, item) #验证单挑记录是否存在 
            # if exist is True:
            #     return False,'item is exist'
        else:
            pass

        return True,'success'

    #洗数据
    def buildItem(self,item,spider):

        #洗liuli 数据
        if spider =='liuli':
            # #翻译title
            # youdao = Youdao()
            # title = youdao.fanyi(item['title'])
            # if title is not None:
            #     item['title'] = title
            pass
        else:
            pass
        
        item['created_at'] = time.strftime('%Y-%m-%d %H-%I-%S',time.localtime(time.time())) #通用创建时间

        return item



    # #验证琉璃神社记录是否存在 return true or false
    # def checkLiuliExist(self,cursor,item):
        
    #     sql = "select * from july_articles where url = '" + item['url'] +"'"
    #     res = self.do_query_one(cursor,sql)

    #     print('6666666666666')
    #     print(sql)
        

    #     if res == False:
    #         return False
    #     return True

