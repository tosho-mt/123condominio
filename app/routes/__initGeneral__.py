from flask import render_template, request, json, redirect, url_for, flash, session,escape, send_from_directory,g,abort
# from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash #encryptar
import requests
import sys # captura errores
import os #ruta absoluta para subir archivos 
from app import app
from app.routes.__initDb__ import *


#personas
@app.route('/MantPersonas',methods=['POST','GET'])
def MantPersonas():
        try:                  
                if request.method == 'POST':
                        BuscarPor = request.form['BuscarPor']
                        txtbuscar = request.form['txtbuscar']
                        
                        if BuscarPor == "1":
                                personas = consTabla('select CodPersona, cedula, Apellidos, Nombres, FechaNacimiento, Genero, Estado, usuarioMod, fechaMod from personas where cedula like "%'+ txtbuscar + '%"')
                        if BuscarPor == "2":
                                personas = consTabla('select CodPersona, cedula, Apellidos, Nombres, FechaNacimiento, Genero, Estado, usuarioMod, fechaMod from personas where Apellidos like "%'+ txtbuscar + '%"')
                        if BuscarPor == "3":
                                personas = consTabla('select CodPersona, cedula, Apellidos, Nombres, FechaNacimiento, Genero, Estado, usuarioMod, fechaMod from personas where Nombres like "%'+ txtbuscar + '%"')
                                
                        return render_template("/General/MantPersonas.html",personas=personas)
                else:
                        if g.nameSisfiab:
                                if int(g.TipoUsuSisfiab) >= 3:
                                        personas = consTabla('select CodPersona, cedula, Apellidos, Nombres, FechaNacimiento, Genero, Estado, usuarioMod, fechaMod from personas')
                                        return render_template("/General/MantPersonas.html",personas=personas)
                                else:
                                        return render_template('home.html')
                        else:
                                return render_template('login.html')
        except Exception as e:
                flash(e)
                return render_template('/General/MantPersonas.html')

@app.route('/Persona/<idPersona>')
def Persona(idPersona):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:                       
                                if idPersona == "0":
                                        return render_template("/General/Persona.html",persona=idPersona)
                                else:
                                        persona=  consTablaPara('select CodPersona, cedula, Apellidos, Nombres, (concat(substring(FechaNacimiento,1,4) , "-" , substring(FechaNacimiento,5,2) , "-" ,substring(FechaNacimiento,7,2))) as FechaNacimiento, Genero, Estado from personas where CodPersona = %s' ,[idPersona])
                                        return render_template("/General/Persona.html",persona=persona)                        
                        else:
                                return render_template("/Inicio.html")
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/General/Persona.html',persona=idPersona)

@app.route('/addPersonas/<string:idPersonas>',methods=['POST'])
def addPersonas(idPersonas):
        try:
                if request.method == 'POST':                        
                        
                        apellidos = request.form['apellidos']
                        nombres = request.form['nombres']
                        fechaNacimiento = request.form['fechaNacimiento']
                        fechaNacimiento = fechaNacimiento.replace("-","")
                        tipoGenero = request.form['tipoGenero']
                        if tipoGenero == "1":
                                tipoGenero = "Masculino"
                        else:
                                tipoGenero = "Femenino"
                        
                        
                        if idPersonas == "0":
                                cedula = request.form['cedula']
                                consInsTabla("INSERT INTO personas (cedula, Apellidos, Nombres, FechaNacimiento, Genero, Estado, usuarioMod, fechaMod) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",[cedula, apellidos, nombres, fechaNacimiento,tipoGenero,'Activo',session['idUsuSisfiab'],g.fechaNum ])
                        else:     
                                consUpdTabla('UPDATE personas set Apellidos=%s, Nombres=%s, FechaNacimiento=%s, Genero=%s, usuarioMod=%s,fechaMod=%s where CodPersona=%s',[apellidos,nombres, fechaNacimiento,tipoGenero,session['idUsuSisfiab'],g.fechaNum ,idPersonas])
                        
                        if session['pathPersonas'] != "":
                                codpersona = consTablaPara("select codpersona from personas as p where cedula = %s",[cedula])
                                varpath = session['pathPersonas'].split("/")                             
                                return redirect(url_for('NuevoCopropietario', idReside=varpath[1],idPropiedad=varpath[2],idPersona=str(codpersona[0][0])))
                        else:
                                return redirect(url_for('MantPersonas'))
        except Exception as e:
                flash(e)
                return render_template('/General/Persona.html',persona=idPersonas)

