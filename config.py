import os #ruta absoluta para subir archivos 


class config(object):
    DEBUG = False
    MYSQL_DATABASE_HOST='localhost'
    MYSQL_DATABASE_USER='root'
    MYSQL_DATABASE_PASSWORD='SisFiab'
    MYSQL_DATABASE_DB='condominio'
    UPLOAD_FOLDER = os.path.abspath("./app/static/Doc/logos")
    UPLOAD_FOLDERDoc = os.path.abspath("./app/static/Doc/Documentos")

class productionConfig(config):
    DEBUG = False
    MYSQL_DATABASE_HOST='localhost'
    MYSQL_DATABASE_USER='root'
    MYSQL_DATABASE_PASSWORD='SisFiab'
    MYSQL_DATABASE_DB='condominio'
    UPLOAD_FOLDER = os.path.abspath("./app/static/Doc/logos")
    UPLOAD_FOLDERDoc = os.path.abspath("./app/static/Doc/Documentos")


class desarolloConfig(config):
    DEBUG = True

