from flask import Flask, render_template, request, json, redirect, url_for, flash, session,escape, send_from_directory,g,abort
#from flaskext.mysql import MySQL
#from werkzeug.security import generate_password_hash, check_password_hash #encryptar
from datetime import datetime
import sys # captura errores


app = Flask(__name__)
app.config.from_object("config.desarolloConfig") # coje clases del archivo config.py

#settings para configurar las sesiones y poder modificar si fuera el caso
app.secret_key='MtSisFiabAlex'

@app.before_request # se ejecuta al inicio decorador
def before_request():
        if 'nameSisfiab' in session:
                g.nameSisfiab = session['emailSisfiab']
                g.emailSisfiab = session['emailSisfiab']
                g.idUsuSisfiab = session['idUsuSisfiab']
                g.TipoUsuSisfiab = session['TipoUsuSisfiab']
                g.CodCondominio = session['CodCondominio']
        else:
                g.nameSisfiab = None
                g.emailSisfiab = None
                g.idUsuSisfiab = None
                g.TipoUsuSisfiab = None
                g.CodCondominio = None
        g.fechacompleta = datetime.now()
        g.fecha = g.fechacompleta.strftime("%d-%m-%Y") 
        g.fechaNum = g.fechacompleta.strftime("%Y%m%d") 
        g.hora =  g.fechacompleta.strftime("%H:%M:%S")  # ver si se refresca la hora


#controlar errores rutas no existentes y mas
@app.errorhandler(404)
def page_not_found(err):
        return render_template("page_not_found.html"),404

# iportamos las rutas para poder utilizar
from app.routes import *

