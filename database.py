import sqlite3
import re

class db():
    def __init__(self):
       self.__conn = sqlite3.connect("ip.db")
   
    def create(self):
       c = self._conn.cursor()
       c.execute('''CREATE TABLE ip_table
            (ID INT AUTO_INCREMENT PRIMARY KEY,
            ip CHAR(50));''')
       print("Table created successfully")
       self.__conn.commit()
      
    def insert(self,ip):
       c = self.__conn.cursor()
       c.execute('''INSERT INTO ip_table (ip) \
            VALUES ('%s');''' %(ip))
       print("insert data successfully")
       self.__conn.commit()
      

    def getbyIp(self,ip):
       c = self.__conn.cursor()
       cursor = c.execute("SELECT * from ip_table")
       for row in cursor:
          if self.match(row[1],ip):
             return True

          return False

    def match(self,a,b):
       pattern = re.compile(a)
       res = pattern.findall(b)
       if len(res) > 0:
           return True
       else:
           return  False

    def getall(self):
       c = self.__conn.cursor()
       cursor = c.execute("SELECT * from ip_table")
       for row in cursor:
          print(row[0],row[1])



if __name__ == "__main__":
    db = db()
    db.getall()
    #db.insert("221.212.180.*")
    #print(db.getbyIp("221.212.189.29"))