from flaskext.mysql import MySQL
from app import app

mysql = MySQL()
mysql.init_app(app)

# funciones
def consTablaPara(sql,parametros):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql,(parametros))
        data = cursor.fetchall()
        cursor.close()
        return data

def consTabla(sql):
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        return data

def consInsTabla(sql,parametros):  
        #print(sql)
        #print(parametros) 
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql ,(parametros))
        conn.commit()
        return 'ok'

def consUpdTabla(sql,parametros):
        #print(parametros)
        #print(sql)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql,(parametros))
        conn.commit()
        return 'ok'
