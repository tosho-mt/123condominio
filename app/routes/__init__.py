
from flask import render_template, request, json, redirect, url_for, flash, session,escape, send_from_directory,g,abort
# from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash #encryptar
import requests
import sys # captura errores
import os # ruta absoluta para subir archivos 
from app import app
from uuid import uuid4 # genera una clave unica cada ves que lo ejecutas
from app.routes.__initDb__ import *
from app.routes.__initAdm__ import *
from app.routes.__initDir__ import *
from app.routes.__initGeneral__ import *

# mysql = MySQL()
# mysql.init_app(app)

@app.route('/')
def home():
        return render_template("home.html")

@app.route('/tarifas')
def tarifas():
        try:
            data = ""
            data = consTabla('select * from tarifas where estado = "Activo" order by idtarifas')
            return render_template("tarifas.html",tarifas=data)
        except Exception as e:
            flash(e)
            return render_template("tarifas.html",tarifas=data)

@app.route('/nuevaTarifa',methods=["GET","POST"])
def nuevaTarifa():
        try:
                if g.nameSisfiab:
                    if g.TipoUsuSisfiab|int() == 5:
                        return render_template('/nuevaTarifa.html')
                    else:
                        return render_template('/Home.html')
                else: 
                        return render_template('/login.html')
        except Exception as e:
                flash(e)
                return redirect(url_for('nuevaTarifa'))
               

@app.route('/add-tarifa',methods=['POST'])
def add_tarifa():
        try:
                if request.method == 'POST':
                        nombre = request.form['nombre'] 
                        descripcion = request.form['descripcion']   
                        tipoTarifa = request.form['tipoTarifa'] 
                        planInicial = request.form['planInicial'] 
                        planBasico = request.form['planBasico'] 
                        planIntermedio = request.form['planIntermedio'] 
                        planSuperior = request.form['planSuperior']       
                        data = consInsTabla('INSERT INTO tarifas (NombreTarifa,PlanInicial, PlanBasico, PlanIntermedio, PlanSuperior, TipoTarifa, Descripcion,Estado, FechaMod, UsuarioMod) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[nombre,planInicial,planBasico,planIntermedio,planSuperior,tipoTarifa,descripcion,'Activo',g.fechaNum,session['idUsuSisfiab']])
                        if len(data) is 0:
                                flash('proceso ok')
        
                        return redirect(url_for('tarifas'))
        except Exception as e:
                flash(e)
                return redirect(url_for('nuevaTarifa'))

@app.route('/elimina-tarifas/<id>')
def elimina_tarifas(id):
        try:
                consUpdTabla('update tarifas set estado ="Eliminado",FechaMod=%s,UsuarioMod=%s where idTarifas =%s', [g.fechaNum,session['idUsuSisfiab'],id])
                flash('Eliminado')
                return redirect(url_for('tarifas'))
        except Exception as e:
                flash(e)
                return redirect(url_for('tarifas'))

#registro usuarios web
@app.route('/registrar', methods=["GET", "POST"])
def registrar():
        try:
                if g.nameSisfiab:
                        return render_template('home.html')
                else:                               
                        if request.method == 'GET':
                                return render_template("register.html")
                        else:
                                
                                print('fecha' + g.fechaNum)
                                nombre = request.form['nombre']
                                email = request.form['email']
                                celular = request.form['celular']
                                password = generate_password_hash( request.form['clave'].encode('utf-8'),method="sha256")
                                consInsTabla('INSERT INTO usuarios (Nombre, Email, Clave, TipoUsuario, Estado, fechaing, CodCondominio, celular,usuarioIng,UsuarioMod,public_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[nombre,email,password,'1','Activo',g.fechaNum,0,celular,7,0,str(uuid4())])
                                user = consTablaPara("SELECT * FROM usuarios WHERE email=%s ",email)
                                session['nameSisfiab'] = user[0][1]
                                session['emailSisfiab'] = user[0][2]
                                session['idUsuSisfiab'] = user[0][0]
                                session['TipoUsuSisfiab'] = user[0][4]
                                session['CodCondominio'] = user[0][7]
                                return redirect(url_for('home'))
        except Exception as e:
                flash(e)
                return render_template('register.html')

@app.route('/login',methods=["GET","POST"])
def login():
        try:                        
                if g.nameSisfiab:
                        return render_template('home.html')
                else:
                        if request.method == 'POST':
                                email = request.form['email']
                                user = consTablaPara("SELECT * FROM usuarios WHERE email=%s ",email)
                                if user and check_password_hash(user[0][3],request.form['password'].encode('utf-8')):
                                        session['nameSisfiab'] = user[0][1]
                                        session['emailSisfiab'] = user[0][2]
                                        session['idUsuSisfiab'] = user[0][0]
                                        session['TipoUsuSisfiab'] = user[0][4]
                                        session['CodCondominio'] = user[0][7]
                                        return render_template('home.html')
                                else:
                                        flash('Usuario o clave incorrectos')
                                        return render_template('login.html')
                        else:
                                return render_template('login.html')
        except Exception as e:
                flash(e)
                return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    session.pop('nameSisfiab',None)
    session.pop('emailSisfiab',None)
    session.pop('idUsuSisfiab',None)
    session.pop('TipoUsuSisfiab',None)
    session.pop('CodCondominio',None)
    return render_template("home.html")



