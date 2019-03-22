#mysql
import pymysql
import time

class Db(object):
    CONNECT = ''
    HOST = 'localhost'
    USER_NAME = 'root'
    USER_PASS = 'root'
    PORT = 3306
    DB = 'july'
    cursor = None #游标
    PREFIX = 'july_' #表前缀

    #初始化
    def __init__(self):
        try:
            self.connect = pymysql.connect(host=self.HOST,user=self.USER_NAME,password=self.USER_PASS,port=self.PORT,db=self.DB)
        except pymysql.err.OperationalError as err:
            print(err)

    #获得mysql操作游标
    def __get_cursor(self):
         if self.cursor is None:
             self.cursor = self.connect.cursor()
             return self.cursor
         else:
             return self.cursor

    #close
    def __close(self):
        self.connect.close()
    
    #commit
    def __commit(self):
        self.connect.commit()

    #rollback
    def __rollback(self):
        self.connect.rollback()

    #添加(self,table,data)
    def insert(self,**kwargs):
        
        table = kwargs["table"] #操作数据表
        keys = ",".join(kwargs["data"].keys()) #添加数据key
        values = ",".join(["%s"]* len(kwargs["data"])) #重复多个%s占位符

        sql = 'insert into '+self.PREFIX+'{table}({keys}) values({values})'.format(table=table,keys=keys,values=values)

        try:
            cursor = self.__get_cursor()
            cursor.execute(sql,tuple(kwargs["data"].values()))
            self.__commit()
            id = cursor.lastrowid #获得添加自增id
            return id
        except pymysql.err.ProgrammingError as err:
            self.__rollback()
            print(err)

        self.__close()

    #更新 带主键更新
    def update(self,**kwargs):

        table = kwargs["table"] #操作数据表
        keys = ",".join(kwargs["data"].keys()) #添加数据key
        values = ",".join(["%s"]* len(kwargs["data"])) #重复多个%s占位符

        #存在则更新 不存在添加
        sql = "insert into "+self.PREFIX+"{table}({keys}) values({values}) ON DUPLICATE KEY UPDATE".format(table=table,keys=keys,values=values)
        #组成更新数据sql
        update = ','.join([" {key} = %s " . format(key = key) for key in kwargs["data"]])
        sql += update

        print(sql)

        try:
            cursor = self.__get_cursor()
            cursor.execute(sql,tuple(kwargs["data"].values())*2)
            self.__commit()

            key = kwargs["data"].keys()
            if 'id' in key:#更新 返回受影响记录
                return cursor.rowcount
            else:#添加
                id = cursor.lastrowid #获得添加自增id
                return id

        except pymysql.err.ProgrammingError as err:
            self.__rollback()
            print(err)

        self.__close()
            

    #删除
    def delete(self,**kwargs):

        table = kwargs["table"]
        condition = kwargs["condition"] #这里可以优化 buildCondition

        sql = "delete from "+self.PREFIX+"{table} where {condition}".format(table = table,condition =condition)

        try:
            cursor = self.__get_cursor()
            cursor = cursor.execute(sql)
            self.__commit()
        except pymysql.err.ProgrammingError as err:
            self.__rollback()
            print(err)

        self.__close()

    #查询单条记录
    def find(self,**kwargs):
        result = self.query(kwargs["table"],kwargs["params"])
        return result[0]
    
    #查询
    def query(self,table,params=None):
        
        sql = self.bulidQuerySql(table,params)
        
        cursor = self.__get_cursor()

        try:
            cursor.execute(sql)
            row = cursor.fetchone()

            result = []

            result.append(row)

            while row:
                row = cursor.fetchone()
                if row is None:
                    break
                result.append(row)
            return result   

        except pymysql.err.ProgrammingError as err:
            print(err)

        self.__close()
    
    #构建查询sql
    def bulidQuerySql(self,table,params):

        sql = "select"

        if params and type(params) is dict:

            if params["field"]==True: #查询全部字段
                sql+= " * "
            else: #拼接field字段
                sql+= ",".join(params["field"])
            
            sql+= "from " + self.PREFIX + table
            
            if "where" in params:
                sql += " where "+ params["where"]

            if "limit" in params:
                sql += " limit "+ params["limit"]

            if "order" in params:
                sql += " order by "+ params["order"]

            if "group" in params:
                sql += " group "+ params["group"]    

        else:
            
            sql += " * from " + self.PREFIX + table
        
        return sql

     #测试
    def test(self):
        res = self.find(table='articles',params={'where':'id = 20','field':True})
        

#test
r = Db()
#dicts = {'title':'cx2','content':'dddddd2','created_at':time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}

#print(r.insert(table='articles',data=dicts)) #测试添加

r.test() #获得数据

#dicts2 = {'id':56,'title':'c22222222444x234','content':'dddddd2'}

#测试更新
#print(r.update(table='articles',data=dicts2))

#测试删除

#print(r.delete(table="articles",condition="id = 53"))

#查询单条数据

