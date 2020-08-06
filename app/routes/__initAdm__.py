from flask import render_template, request, json, redirect, url_for, flash, session,escape, send_from_directory,g,abort
# from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash #encryptar
import requests
import sys # captura errores
import os #ruta absoluta para subir archivos 
from app import app
from app.routes.__initDb__ import *
import time


#Conjunto recidenial
@app.route('/MantconjRecidencial')
def mant_conj_residencial():
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5:
                                data = consTabla('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo,estado,fechamod,usuariomod,fechaing,(select count(*) from etapas where estado = "Activo" and etapas.idcondominio = condominio.idcondominio) as Etapas,(select count(*) from multas where codresidencia = idcondominio) as multas,(select count(*) from bancos where codResidencia =idcondominio) as bancos from condominio where estado = "Activo"')
                                return render_template("/Administrador/MantConjResid.html",condominios=data)
                        else:
                                if int(g.TipoUsuSisfiab) >=3:
                                        data = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo,estado,fechamod,usuariomod,fechaing,(select count(*) from etapas where estado = "Activo" and etapas.idcondominio = condominio.idcondominio) as Etapas,(select count(*) from multas where codresidencia = idcondominio) as multas,(select count(*) from bancos where codResidencia =idcondominio) as bancos from condominio where estado = "Activo" and idCondominio = %s',[g.CodCondominio])
                                        return render_template("/Administrador/MantConjResid.html",condominios=data)
                                else:
                                        return render_template('home.html')
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/MantConjResid.html')

@app.route('/conjRecidencial/<id>')
def conj_residencial(id):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:                       
                                if id == "0":
                                        return render_template("/Administrador/ConjResidencial.html",condominio="0")
                                else:
                                        data=  consTablaPara('select * from condominio where estado = "Activo" and idCondominio = %s' ,[id])
                                        return render_template("/Administrador/ConjResidencial.html",condominio=data[0])                        
                        else:
                                return render_template("/Inicio.html")
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/ConjResidencial.html')

@app.route('/addConjRecidencial/<string:id>',methods=['POST'])
def add_conj_residencial(id):
        try:
                if request.method == 'POST':                        
                        nombre = request.form['nombre']
                        coords = request.form['coords']
                        coords = coords[1:-1].split(',')
                        latitud = coords[0]
                        longitud = coords[1]
                        telefono = request.form['telefono']
                        #cargar el archivo en el directorio
                        f =  request.files["logo"] 
                        #print(f.value)                               
                        if f:
                                filename = f.filename    
                                f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))                                                              
                        else:
                                filename = ""
                        imgAnt = request.form['logoh']
                        if filename == "":
                                filename = imgAnt

                        paginaweb = request.form['paginaweb']
                        
                        if id == "0":
                                ruc = request.form['ruc']
                                consInsTabla('INSERT INTO condominio (Ruc,Nombre, latitud, longitud, telefono, Paginaweb,logo,Estado, fechamod, UsuarioMod,fechaing) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[ruc,nombre,latitud, longitud,telefono, paginaweb,filename,'Activo',g.fechaNum ,session['idUsuSisfiab'],g.fechaNum])
                                sql = 'select idCondominio from condominio where Ruc = %s and Nombre = %s and latitud = %s and longitud = %s'
                                idReside = consTablaPara(sql,[ruc,nombre,latitud, longitud]) 
                                consInsTabla("INSERT INTO etapas (nombreetapa,idcondominio,descripcionetapa,estado,fechamod, UsuarioMod) VALUES (%s,%s,%s,%s,%s,%s)",['Comunal',idReside,'Etapa comunal que todo conjunto tienen','Activo',g.fechaNum ,session['idUsuSisfiab']])                               
                                #crear bano caja chica
                                consInsTabla("INSERT INTO bancos (Nombre, TipoCta, NroCta, Estado, UsuarioMod, fechaMod, codResidencia) VALUES (%s,%s,%s,%s,%s,%s,%s)",["CAJA CHICA",0,0,'Activo',session['idUsuSisfiab'],g.fechaNum ,idReside])
                        else:        
                                consUpdTabla('UPDATE condominio set Nombre=%s, latitud=%s, longitud=%s, telefono=%s, Paginaweb=%s,logo=%s, fechamod=%s, UsuarioMod=%s where idcondominio=%s',[nombre,latitud, longitud,telefono, paginaweb,filename,g.fechaNum ,session['idUsuSisfiab'],id])
                        return redirect(url_for('mant_conj_residencial'))
        except Exception as e:
                flash(e)
                return render_template('/Administrador/ConjResidencial.html')

@app.route('/suspenderCondominio/<string:id>',methods=['GET'])
def suspenderCondominio(id):
        try:
                if request.method == 'GET':
                        consUpdTabla('UPDATE condominio set estado="Suspendido", fechamod=%s, UsuarioMod=%s where idcondominio=%s',[g.fechaNum ,session['idUsuSisfiab'],id])
                        return redirect(url_for('mant_conj_residencial'))

        except Exception as e:
                flash(e)
                return render_template('/Administrador/MantConjResid.html')


#Documentos
@app.route('/MantDocumentos/<string:id>')
def MantDocumentos(id):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:
                                sql = 'select *,(select valor from parametros where estado = "Activo" and coddefinicion = "TipoDocumento" and codigo = tipodocumento)  from Documentos where estado = "Activo" and idcondominio = %s order by tipodocumento, numero'
                                data = consTablaPara(sql,[id])
                                sql = 'select nombre,idcondominio from condominio where condominio.idcondominio = %s'
                                residencia = consTablaPara(sql,[id])
                                return render_template("/Administrador/MantDocumentos.html",documentos=data,residencia=residencia)
                        else:
                                return render_template('Inicio.html')
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/MantDocumentos.html')

@app.route('/documentos/<id>')
def documentos(id):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:
                                vid = id.split('-')
                                tipodocs = consTabla('select codigo,valor from parametros where estado = "Activo" and coddefinicion = "TipoDocumento" and codigo > 0 order by codigo')
                                sql = 'select nombre,idcondominio from condominio where condominio.idcondominio = %s'
                                residencia = consTablaPara(sql,[vid[0]])
                                if vid[1] == "0":
                                        return render_template("/Administrador/documentos.html",documento=vid[1],conjunto=residencia,tipodocs = tipodocs)
                                else:
                                        data=  consTablaPara('select * from Documentos where estado = "Activo" and idDocumento = %s' ,[vid[1]])
                                        return render_template("/Administrador/documentos.html",documento=data,conjunto=residencia,tipodocs = tipodocs)                        
                        else:
                              return render_template('Inicio.html')  
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/documentos.html')

@app.route('/addDocumentos/<string:id>',methods=['POST'])
def addDocumentos(id):
        try:
                if request.method == 'POST':  
                        vId = id.split('-')                   
                        tipoDocumento = request.form['tipoDocumento']

                        nrodoc = request.form['nrodoc']

                        comentario = request.form['comentario']

                        #cargar el archivo en el directorio
                        f =  request.files["logo"]                             
                        if f:
                                filename = f.filename                                
                                f.save(os.path.join(app.config['UPLOAD_FOLDERDoc'],filename))                         
                        else:
                                filename = ""

                        doch = request.form['doch']
                        if filename == "":
                                filename = doch

                        seguridad = request.form['seguridad']
                        
                        if vId[1] == "0":
                                consInsTabla('INSERT INTO documentos (idcondominio,tipodocumento, numero,comentario,fechacarga, documento,estado,nivelseguridad,fechamod, UsuarioMod) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',[vId[0],tipoDocumento,nrodoc, comentario,g.fechaNum, filename,'Activo',seguridad,g.fechaNum ,session['idUsuSisfiab']])
                        else:    
                                print('Temporal hasta el update') 
                                #consUpdTabla('UPDATE documentos set Nombre=%s, latitud=%s, longitud=%s, telefono=%s, Paginaweb=%s,logo=%s, fechamod=%s, UsuarioMod=%s where idcondominio=%s',[nombre,latitud, longitud,telefono, paginaweb,filename,fechaNum ,session['idUsuSisfiab'],vId[1]])
                        return redirect(url_for('MantDocumentos',id=vId[0]))
        except Exception as e:
                flash(e)
                return render_template('/Administrador/Documentos.html')


#Etapas
@app.route('/MantEtapas/<string:id>')
def MantEtapas(id):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:                                
                                sql = 'select idEtapas, NombreEtapa, idCondominio, DescripcionEtapa, Estado,(SELECT count(*) FROM necesidades where necesidades.idetapa = idetapas and idresidencia = idcondominio and necesidades.estado = "Activo") as nronecesidades,(select count(*) from propiedad where estado = "Activo" and propiedad.idetapas = etapas.idEtapas and idresidencia = idCondominio) as nroPropiedades  from etapas where estado = "Activo" and idcondominio = %s'
                                data = consTablaPara(sql,[id])
                                sql = 'select nombre,idcondominio from condominio where condominio.idcondominio = %s'
                                residencia = consTablaPara(sql,[id])
                                return render_template("/Administrador/MantEtapas.html",Etapas=data,residencia=residencia)
                        else:
                                return render_template('Inicio.html')
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/MantEtapas.html')

@app.route('/etapas/<string:idReside>/<string:idEtapa>')
def etapas(idReside,idEtapa=0):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:
                                sql = 'select nombre,idcondominio from condominio where condominio.idcondominio = %s'
                                residencia = consTablaPara(sql,[idReside])
                                if idEtapa == "0":
                                        return render_template("/Administrador/etapas.html",etapa=idEtapa,conjunto=residencia)
                                else:
                                        data=  consTablaPara('select * from etapas where estado = "Activo" and idetapas = %s' ,[idEtapa])
                                        return render_template("/Administrador/etapas.html",etapa=data,conjunto=residencia)                        
                        else:
                              return render_template('Inicio.html')  
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/etapas.html')

@app.route('/addEtapas/<string:idReside>/<string:idEtapa>',methods=['POST'])
def addEtapas(idReside,idEtapa=0):
        try:
                if request.method == 'POST':                 
                        nombre = request.form['nombre']
                        descripcion = request.form['descripcion']
                        if idEtapa == "0":
                                consInsTabla("INSERT INTO etapas (nombreetapa,idcondominio,descripcionetapa,estado,fechamod, UsuarioMod) VALUES (%s,%s,%s,%s,%s,%s)",[nombre,idReside,descripcion,'Activo',g.fechaNum ,session['idUsuSisfiab']])
                        else:    
                                consUpdTabla('UPDATE etapas set nombreetapa=%s, descripcionetapa=%s, fechamod=%s, UsuarioMod=%s where idetapas=%s',[nombre,descripcion,g.fechaNum ,session['idUsuSisfiab'],idEtapa])
                        return redirect(url_for('MantEtapas',id=idReside))
        except Exception as e:
                flash(e)
                return render_template('/Administrador/Etapas.html')

@app.route('/suspenderEtapas/<string:idEtapa>/<string:idReside>',methods=['GET'])
def suspenderEtapas(idEtapa,idReside):
        try:
                if request.method == 'GET':
                        consUpdTabla('UPDATE etapas set estado="Suspendido", fechamod=%s, UsuarioMod=%s where idetapas=%s',[g.fechaNum ,session['idUsuSisfiab'],idEtapa])
                        return redirect(url_for('MantEtapas',id=idReside))

        except Exception as e:
                flash(e)
                return render_template('/Administrador/MantConjResid.html')


#Multas
@app.route('/MantMultas/<string:id>')
def MantMultas(id):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:                                
                                sql = 'select CodMulta, codResidencia, Descripcion, valor, porcentaje, estado from multas where codResidencia = %s'
                                data = consTablaPara(sql,[id])
                                sql = 'select nombre,idcondominio from condominio where condominio.idcondominio = %s'
                                residencia = consTablaPara(sql,[id])
                                return render_template("/Administrador/MantMultas.html",Multas=data,residencia=residencia)
                        else:
                                return render_template('Inicio.html')
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/MantMultas.html')

@app.route('/multas/<string:idReside>/<string:idmulta>')
def multas(idReside,idmulta=0):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:
                                sql = 'select nombre,idcondominio from condominio where condominio.idcondominio = %s'
                                residencia = consTablaPara(sql,[idReside])
                                if idmulta == "0":
                                        return render_template("/Administrador/multas.html",multa=idmulta,conjunto=residencia)
                                else:
                                        data=  consTablaPara('select CodMulta, codResidencia, Descripcion, valor, porcentaje, estado from multas where CodMulta = %s' ,[idmulta])
                                        return render_template("/Administrador/multas.html",multa=data,conjunto=residencia)                        
                        else:
                              return render_template('Inicio.html')  
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/multas.html')

@app.route('/addMultas/<string:idReside>/<string:idMulta>',methods=['POST'])
def addMultas(idReside,idMulta=0):
        try:
                if request.method == 'POST':                 
                        
                        descripcion = request.form['descripcion']
                        valor = request.form['valor']
                        porcentaje = request.form['porcentaje']

                        if porcentaje =="":
                                porcentaje = 0
                        if valor =="":
                                valor = 0
                        if idMulta == "0":
                                consInsTabla("INSERT INTO multas ( codResidencia, estado, Descripcion, valor, porcentaje, fechamod, usuariomod) VALUES (%s,%s,%s,%s,%s,%s,%s)",[idReside,'Activo',descripcion,valor, porcentaje,g.fechaNum ,session['idUsuSisfiab']])
                        else:    
                                consUpdTabla('UPDATE multas set Descripcion=%s,valor=%s,porcentaje=%s, fechamod=%s, usuariomod=%s where codmulta=%s',[descripcion,valor,porcentaje,g.fechaNum ,session['idUsuSisfiab'],idMulta])
                        return redirect(url_for('MantMultas',id=idReside))
        except Exception as e:
                flash(e)
                return render_template('/Administrador/multas.html')


@app.route('/suspenderMultas/<string:idMulta>/<string:idReside>',methods=['GET'])
def suspenderMultas(idMulta,idReside):
        try:
                if request.method == 'GET':
                        consUpdTabla('UPDATE multas set estado="Suspendido", fechamod=%s, UsuarioMod=%s where codmulta=%s',[g.fechaNum ,session['idUsuSisfiab'],idMulta])
                        return redirect(url_for('MantMultas',id=idReside))

        except Exception as e:
                flash(e)
                return render_template('/Administrador/MantMultas.html')

#Bancos
@app.route('/MantBancos/<string:id>')
def MantBancos(id):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:                                
                                sql = 'select CodBanco, Nombre, TipoCta, NroCta, Estado, UsuarioMod, fechaMod, codResidencia,(select Valor from parametros where CodDefinicion = "TipoCta" and Codigo =TipoCta) as tipoCtades, 0 as consiliado, 0 as sinconsiliars from bancos where codResidencia = %s'
                                bancos = consTablaPara(sql,[id])
                                sql = 'select nombre,idcondominio from condominio where condominio.idcondominio = %s'
                                residencia = consTablaPara(sql,[id])
                                return render_template("/Administrador/MantBancos.html",bancos=bancos,residencia=residencia)
                        else:
                                return render_template('Inicio.html')
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return redirect(url_for('MantBancos',id=id))

@app.route('/Bancos/<string:idReside>/<string:idbanco>')
def Bancos(idReside,idbanco=0):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:
                                sql = 'select nombre,idcondominio from condominio where condominio.idcondominio = %s'
                                residencia = consTablaPara(sql,[idReside])
                                tipoctas = consTabla("select Codigo,Valor from parametros where CodDefinicion = 'TipoCta' and estado = 'Activo'")
                                if idbanco == "0":
                                        return render_template("/Administrador/bancos.html",banco=idbanco,conjunto=residencia,tipoctas=tipoctas)
                                else:
                                        data=  consTablaPara('select CodBanco, Nombre, TipoCta, NroCta, Estado, UsuarioMod, fechaMod, codResidencia from bancos where CodBanco = %s' ,[idbanco])
                                        return render_template("/Administrador/bancos.html",banco=data,conjunto=residencia,tipoctas=tipoctas)                        
                        else:
                              return render_template('Inicio.html')  
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return redirect(url_for('Bancos',idReside=idReside,idbanco=idbanco))

@app.route('/addbanco/<string:idReside>/<string:idbanco>',methods=['POST'])
def addbanco(idReside,idbanco=0):
        try:
                if request.method == 'POST':                 
                        
                        Nombre = request.form['Nombre']
                        tipoCta = request.form['tipoCta']
                        numerocta = request.form['numerocta']
                        if idbanco == "0":
                                consInsTabla("INSERT INTO bancos (  Nombre, TipoCta, NroCta, Estado, UsuarioMod, fechaMod, codResidencia) VALUES (%s,%s,%s,%s,%s,%s,%s)",[Nombre,tipoCta,numerocta,'Activo',session['idUsuSisfiab'],g.fechaNum ,idReside])
                        else:    
                                consUpdTabla('UPDATE bancos set Nombre=%s,TipoCta=%s,NroCta=%s, fechamod=%s, usuariomod=%s where CodBanco=%s',[Nombre,tipoCta,numerocta,g.fechaNum ,session['idUsuSisfiab'],idbanco])
                        return redirect(url_for('MantBancos',id=idReside))
        except Exception as e:
                flash(e)
                return redirect(url_for('Bancos',idReside=idReside,idbanco=idbanco))

@app.route('/suspenderBanco/<string:idBanco>/<string:idReside>',methods=['GET'])
def suspenderBanco(idBanco,idReside):
        try:
                if request.method == 'GET':
                        consUpdTabla('UPDATE bancos set estado="Suspendido", fechamod=%s, UsuarioMod=%s where CodBanco=%s',[g.fechaNum ,session['idUsuSisfiab'],idBanco])
                        return redirect(url_for('MantBancos',id=idReside))

        except Exception as e:
                flash(e)
                return redirect(url_for('MantBancos',id=idReside))



#Necesidades
@app.route('/MantNecesidades/<string:idReside>/<string:idetapa>')
def MantNecesidades(idReside,idetapa):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:
                                sql = 'select idNecesidad, IdEtapa, IdResidencia,(select valor from parametros where estado = "Activo" and coddefinicion = "TipoProvision" and codigo = tipo) as tipo, nombre, descripcion, fechaIni, fechaUltMant, fechaGarantia, precio, tiempoEntreMante, NroIdNecesidad, estado,tipo from necesidades where estado = "Activo" and IdResidencia= %s and IdEtapa = %s'
                                data = consTablaPara(sql,[idReside,idetapa])                               
                                sql = 'select idEtapas,NombreEtapa from etapas where estado = "Activo" and idcondominio = %s and idEtapas = %s'
                                etapa = consTablaPara(sql,[idReside,idetapa])
                                sql = 'select nombre,idcondominio from condominio where condominio.idcondominio = %s'
                                residencia = consTablaPara(sql,[idReside])
                                return render_template("/Administrador/MantNecesidades.html",necesidades = data,etapa=etapa,residencia=residencia)
                        else:
                                return render_template('Inicio.html')
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/MantNecesidades.html')

@app.route('/necesidad/<string:idReside>/<string:idEtapa>/<string:idNecesidad>')
def necesidad(idReside,idEtapa,idNecesidad=0):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) >= 3:
                                sql = 'select nombre,idcondominio from condominio where condominio.idcondominio = %s'
                                residencia = consTablaPara(sql,[idReside])
                                sql = 'select idEtapas,NombreEtapa from etapas where estado = "Activo" and idcondominio = %s and idEtapas = %s'
                                etapa = consTablaPara(sql,[idReside,idEtapa])
                                sql = 'select Codigo,Valor from parametros where estado = "Activo" and coddefinicion = "TipoProvision" order by codigo'
                                tipo = consTabla(sql)
                                if idNecesidad == "0":
                                        return render_template("/Administrador/necesidad.html",residensia=residencia,etapa=etapa,necesidad=idNecesidad,tipos=tipo)
                                else:
                                        data=  consTablaPara('select idNecesidad, IdEtapa, IdResidencia, tipo, nombre, descripcion, (concat(substring(fechaIni,1,4) , "-" , substring(fechaIni,5,2) , "-" ,substring(fechaIni,7,2))) as fechaIni, (concat(substring(fechaUltMant,1,4) , "-" , substring(fechaUltMant,5,2) , "-" ,substring(fechaUltMant,7,2))) as fechaUltMant, (concat(substring(fechaGarantia,1,4) , "-" , substring(fechaGarantia,5,2) , "-" ,substring(fechaGarantia,7,2))) as fechaGarantia, precio, tiempoEntreMante, NroIdNecesidad, fechamod, usuarioMod, estado from necesidades where estado = "Activo" and idnecesidad = %s' ,[idNecesidad])
                                        return render_template("/Administrador/necesidad.html",residensia=residencia,etapa=etapa,necesidad=data,tipos=tipo)                        
                        else:
                              return render_template('Inicio.html')  
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/necesidad.html')

@app.route('/addNecesidad/<string:idReside>/<string:idEtapa>/<string:idNecesidad>',methods=['POST'])
def addNecesidad(idReside,idEtapa,idNecesidad=0):
        try:
                if request.method == 'POST':
                        tiponecesidad = request.form['tiponecesidad']                
                        nombre = request.form['nombre']
                        descripcion = request.form['descripcion']
                        fechaIni = request.form['fechaIni'] 
                        fechaIni = fechaIni.replace("-","")
                        fechaUltMant = request.form['fechaUltMant']
                        fechaUltMant = fechaUltMant.replace("-","")
                        fechaGarantia = request.form['fechaGarantia']
                        fechaGarantia = fechaGarantia.replace("-","")
                        Precio = request.form['precio']
                        tiempo = request.form['tiempo']
                        nroNecesidad = request.form['nroNecesidad']
                        if idNecesidad == "0":
                                consInsTabla("INSERT INTO necesidades ( IdEtapa, IdResidencia, tipo, nombre, descripcion, fechaIni, fechaUltMant, fechaGarantia, precio, tiempoEntreMante, NroIdnecesidad, fechamod, usuarioMod, estado) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[idEtapa,idReside,tiponecesidad,nombre,descripcion,fechaIni,fechaUltMant,fechaGarantia,Precio,tiempo,nroNecesidad,g.fechaNum ,session['idUsuSisfiab'],'Activo'])
                        else:    
                                consUpdTabla('UPDATE necesidades set tipo=%s,nombre=%s, descripcion=%s, fechaIni=%s, fechaUltMant=%s, fechaGarantia=%s, precio=%s, tiempoEntreMante=%s, NroIdnecesidad=%s ,fechamod=%s, UsuarioMod=%s where idnecesidad=%s',[tiponecesidad,nombre,descripcion,fechaIni,fechaUltMant,fechaGarantia,Precio,tiempo,nroNecesidad,g.fechaNum ,session['idUsuSisfiab'],idNecesidad])
                        return redirect(url_for('MantNecesidades',idReside=idReside,idetapa=idEtapa))
        except Exception as e:
                flash(e)
                return render_template('/Administrador/necesidad.html')

@app.route('/suspenderNecesidad/<string:idReside>/<string:idEtapa>/<string:idNecesidad>',methods=['GET'])
def suspenderNecesidad(idReside,idEtapa,idNecesidad):
        try:
                if request.method == 'GET':
                        consUpdTabla('UPDATE necesidades set estado="Suspendido", fechamod=%s, UsuarioMod=%s where idnecesidad=%s',[g.fechaNum ,session['idUsuSisfiab'],idNecesidad])
                        return redirect(url_for('MantNecesidades',idReside=idReside,idetapa=idEtapa))

        except Exception as e:
                flash(e)
                return render_template('/Administrador/MantNecesidades.html')




#creacion propiedades
@app.route('/creaPropiedades/<string:idReside>/<string:idEtapa>')
def creaPropiedades(idReside,idEtapa):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) >= 3 and int(g.CodCondominio) == int(idReside)):
                                sql = 'select nombre,idcondominio from condominio where condominio.idcondominio = %s'
                                residencia = consTablaPara(sql,[idReside])
                                sql = 'select idEtapas,NombreEtapa from etapas where estado = "Activo" and idcondominio = %s and idEtapas = %s'
                                etapa = consTablaPara(sql,[idReside,idEtapa])
                                sql = 'select Codigo,Valor from parametros where estado = "Activo" and coddefinicion = "TipoPropiedad" order by codigo'
                                tipo = consTabla(sql)
                                return render_template("/Administrador/creaPropiedades.html",residensia=residencia,etapa=etapa,tipos=tipo)
                        else:
                                return render_template('Inicio.html')  
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/creaPropiedades.html')

@app.route('/addPropiedad/<string:idReside>/<string:idEtapa>',methods=['POST'])
def addPropiedad(idReside,idEtapa):
        try:
                if request.method == 'POST':
                        tipoPropiedad = request.form['tipoPropiedad']                
                        NroPropiedades = request.form['NroPropiedades']
                        nrPropie=1
                        while nrPropie<=int(NroPropiedades):
                                consInsTabla("INSERT INTO propiedad ( idEtapas, idResidencia, TipoPropiedad, Nropropiedad, Estado, FechaMod, UsuarioMod,Nombre) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",[idEtapa,idReside,tipoPropiedad,nrPropie,'Activo',g.fechaNum ,session['idUsuSisfiab'],''])
                                nrPropie=nrPropie+1
                        
                        return redirect(url_for('MantEtapas',id=idReside))
        except Exception as e:
                flash(e)
                return render_template('/Administrador/creaPropiedades.html')


#mantenimiento de Propiedades
@app.route('/MantPropiedades')
def MantPropiedades():
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5:
                                data = consTabla('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo,estado,fechamod,usuariomod,fechaing,(select count(*) from propiedad where estado = "Activo" and propiedad.idResidencia = condominio.idcondominio) as Propiedades from condominio where estado = "Activo"')
                                return render_template("/Administrador/MantPropiedades.html",condominios=data)
                        else:
                                if int(g.TipoUsuSisfiab) >= 3:
                                        return redirect(url_for('Propiedades',idReside=g.CodCondominio))
                                else:   
                                        return render_template('home.html')
                else:
                        return render_template('login.html')      
        except Exception as e:
                flash(e)
                return render_template('/Directorio/MantPropiedades.html')



@app.route('/Propiedades/<string:idReside>')
def Propiedades(idReside):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) >= 3 and int(g.CodCondominio) == int(idReside)):
                                data = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo from condominio where estado = "Activo" and idCondominio = %s',[idReside])        
                                sql = "select (select NombreEtapa from etapas where idCondominio = idResidencia and etapas.idEtapas = propiedad.idEtapas) as Etapa," 
                                sql += "(select valor from parametros where CodDefinicion = 'TipoPropiedad' and codigo = TipoPropiedad) as hTipoPropiedad," 
                                sql += "Nropropiedad,Nombre,metroscuadrados,idPropiedad,idEtapas,idResidencia,(select count(*) from copropietario where estado = 'Activo' and copropietario.codPropiedad = idPropiedad) as NumCopropietario,Arrendada from propiedad where estado = 'activo' and idResidencia = %s order by idEtapas,idPropiedad"
                                propiedades = consTablaPara(sql,[idReside])
                                return render_template("/Administrador/Propiedades.html",condominio=data,propiedades=propiedades)
                        else:
                                return render_template('home.html')
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return redirect(url_for('Propiedades',idReside=g.CodCondominio))


@app.route('/actualisapropiedad/<string:idReside>/<string:idPropiedad>',methods=['POST'])
def actualisapropiedad(idReside,idPropiedad):
        try:
                if request.method == 'POST':
                        
                        nombre = request.form['nombre']                
                        metros = request.form['metros']

                        if request.form.get('arrienda'):
                                arrienda = "SI"
                        else:
                                arrienda = "NO"
                        consUpdTabla('UPDATE propiedad set nombre=%s,metroscuadrados=%s, fechamod=%s, UsuarioMod=%s,Arrendada=%s where idPropiedad=%s',[nombre,metros,g.fechaNum ,session['idUsuSisfiab'],arrienda,idPropiedad])               
                        return redirect(url_for('Propiedades',idReside=idReside))
        except Exception as e:
                flash(e)
                return redirect(url_for('Propiedades',idReside=idReside))

#mantenieito de copropietarios
@app.route('/Copropietarios/<string:idReside>/<string:idPropiedad>')
def Copropietarios(idReside,idPropiedad):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) >= 3 and int(g.CodCondominio) == int(idReside)):
                                data = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo from condominio where estado = "Activo" and idCondominio = %s',[idReside])        
                                sql = "select idPropiedad, Nropropiedad,Nombre from propiedad where estado = 'activo' and idResidencia = %s and idPropiedad = %s order by idEtapas,idPropiedad"
                                propiedad = consTablaPara(sql,[idReside,idPropiedad])
                                sql = "select idCopropietario, cedula, CONCAT(Apellidos, ' ', Nombres) as Nombre, codRecidencia, codPropiedad,(select valor from parametros where CodDefinicion  ='TipoCopropietario' and codigo = Tipo) as TipoCopro,Tipo, (select valor from parametros where CodDefinicion  ='TipoParentesco' and codigo = Parentesco) as TipoParentesco,Parentesco, FechaIngresa, FechaSale, copropietario.Estado, copropietario.FechaMod, copropietario.UsuarioMod from copropietario , personas where personas.CodPersona = copropietario.codPersona and codRecidencia = %s and codPropiedad = %s"
                                copropietarios = consTablaPara(sql,[idReside,idPropiedad])                                
                                return render_template("/Administrador/Copropietarios.html",condominio=data,propiedad=propiedad,copropietarios=copropietarios)
                        else:
                                return render_template('home.html')
                else:
                        return render_template('login.html')  
        except Exception as e:
                flash(e)
                return redirect(url_for('Copropietarios',condominio=data,propiedad=propiedad))


@app.route('/NuevoCopropietario/<string:idReside>/<string:idPropiedad>/<string:idPersona>')
def NuevoCopropietario(idReside,idPropiedad,idPersona=0):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) >= 3 and int(g.CodCondominio) == int(idReside)):
                                sql = 'select Codigo,Valor from parametros where estado = "Activo" and coddefinicion = "TipoCopropietario" order by codigo'
                                tipoCopropietarios = consTabla(sql)
                                sql = 'select Codigo,Valor from parametros where estado = "Activo" and coddefinicion = "TipoParentesco" order by codigo'
                                tipoParentescos = consTabla(sql)
                                residencia = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo from condominio where estado = "Activo" and idCondominio = %s',[idReside])        
                                sql = "select idPropiedad, Nropropiedad,Nombre from propiedad where estado = 'activo' and idResidencia = %s and idPropiedad = %s order by idEtapas,idPropiedad"
                                propiedad = consTablaPara(sql,[idReside,idPropiedad])
                                sql = "select p.CodPersona, CONCAT(Apellidos, ' ', Nombres) as Nombre from personas as p where p.Estado = 'Activo' and not  p.CodPersona in (select codpersona from copropietario where codRecidencia = %s and codPropiedad = %s) order by apellidos"
                                personas = consTablaPara(sql,[idReside,idPropiedad]) 
                                print(idPersona)
                                # creo seccion para regresar
                                session['pathPersonas'] = "NuevoCopropietario/" + idReside + "/" + idPropiedad                    
                                return render_template("/Administrador/NuevoCopropietario.html",tipoCopropietarios=tipoCopropietarios,tipoParentescos=tipoParentescos,residencia=residencia,propiedad=propiedad,personas=personas,idPersona=idPersona)  
                        else:
                              return render_template('Inicio.html')  
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Administrador/NuevoCopropietario.html',idReside=idReside,idPropiedad=idPropiedad)


@app.route('/addCopropietario/<string:idReside>/<string:idPropiedad>',methods=['POST'])
def addCopropietario(idReside,idPropiedad):
        try:
                if request.method == 'POST':
                        persona = request.form['persona']
                        tipocopropietario = request.form['tipocopropietario']                
                        tipoParentesco = request.form['tipoParentesco']
                        fechaIni = request.form['fechaIni'] 
                        fechaIni = fechaIni.replace("-","")
                        consInsTabla("INSERT INTO copropietario (codPersona, codRecidencia, codPropiedad, Tipo, Parentesco, FechaIngresa, FechaSale, Estado, FechaMod, UsuarioMod) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[persona,idReside,idPropiedad,tipocopropietario,tipoParentesco,fechaIni,0,'Activo',g.fechaNum ,session['idUsuSisfiab']])
                        return redirect(url_for('Copropietarios',idReside=idReside,idPropiedad=idPropiedad))
        except Exception as e:
                flash(e)
                return redirect(url_for('NuevoCopropietario',idReside=idReside,idPropiedad=idPropiedad))


#creacion ingresos
@app.route('/MantIngresos')
def MantIngresos():
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5:
                                data = consTabla('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo,estado,fechamod,usuariomod,fechaing,(0) as Alicuotas from condominio where estado = "Activo"')
                                return render_template("/Administrador/MantIngresos.html",condominios=data)
                        else:
                                if int(g.TipoUsuSisfiab) >= 3:
                                        return redirect(url_for('Ingresos',idReside=g.CodCondominio))
                                else:   
                                        return render_template('home.html')
                else:
                        return render_template('login.html')      
        except Exception as e:
                flash(e)
                return render_template('/Administrador/MantIngresos.html')

@app.route('/Ingresos/<string:idReside>')
def Ingresos(idReside):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) >= 3 and int(g.CodCondominio) == int(idReside)):
                                data = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo from condominio where estado = "Activo" and idCondominio = %s',[idReside])        
                                sql = "select (select NombreEtapa from etapas where idCondominio = idResidencia and etapas.idEtapas = propiedad.idEtapas) as Etapa," 
                                sql += "(select valor from parametros where CodDefinicion = 'TipoPropiedad' and codigo = TipoPropiedad) as hTipoPropiedad," 
                                sql += "nombre,Nropropiedad,Nombre,IFNULL((select sum(valor) from ingreso where codpropiedad = idPropiedad),0) as Ingresos,idPropiedad,idEtapas,idResidencia" 
                                sql += ",IFNULL((select sum(valor) from cobros where estado = 'Activo' and codpropiedad = idPropiedad and tipoCobro = 1),0) as Cobros " 
                                sql += ",IFNULL((select sum(valortotal) from cobros where estado = 'Activo' and codIngreso = 0 and codpropiedad = idPropiedad and tipoCobro = 2),0) as Abonos"
                                sql += ",IFNULL((select sum(valor) from cobros where estado = 'Activo' and codIngreso <> 0 and codpropiedad = idPropiedad and tipoCobro = 2) ,0) as Abonoscobrados"                                
                                sql += ",IFNULL((select sum(valor) from cobros where estado = 'Activo' and codIngreso <> 0 and codpropiedad = idPropiedad and tipoCobro = 2 and nrocobro in (select nrocobro from cobros where estado = 'Activo' and codIngreso = 0 and codpropiedad = idPropiedad and tipoCobro = 2)),0) as Abonoscobradospendientes  from propiedad where estado = 'activo' and idResidencia = %s order by idEtapas,idPropiedad"                                
                                propiedades = consTablaPara(sql,[idReside])
                                return render_template("/Administrador/Ingresos.html",condominio=data,propiedades=propiedades)
                        else:
                                return render_template('home.html')
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return redirect(url_for('Ingresos',idReside=g.CodCondominio))


@app.route('/GenAlicuota/<string:idReside>')
def GenAlicuota(idReside):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) >= 3 and int(g.CodCondominio) == int(idReside)):
                                residencia = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo from condominio where estado = "Activo" and idCondominio = %s',[idReside])        
                                sql = "select detCodPresupuesto, codPresupuesto, codEtapa, (select nombreetapa from etapas where idetapas = codetapa) as nombreetapa,codResidencia, gastoTotal, gastoEtapa, gastoComunal, nroRecidencia, metrosCuadrados, nroResidenciaEtapa, metrosCuadradosEtapa,alicuotaSelecionada, "
                                sql = sql + " case alicuotaSelecionada  when 'var' then 'Valor Alicuota por Residencia'  when 'vamc' then 'Valor Alicuota por metro cuadrado'  when 'vare' then 'Valor Alicuota por Residencia y por Etapa' when 'vamce' then 'Valor Alicuota por metro cuadrado y Etapa' end as AlicuotaPor,"
                                sql = sql + " valorAlicuota,necesidades from detpresupuesto where codpresupuesto in (select codpresupuesto from presupuesto where codresidencia = %s and estado = 'Activo')"
                                presupuestos = consTablaPara(sql,[idReside])
                                fechamax = consTablaPara("select COALESCE(max(fecha),0) from ingreso where codrecidencia = %s",[idReside])
                                return render_template("/Administrador/GenAlicuota.html",residencia=residencia,presupuestos=presupuestos,fechamax=fechamax[0][0])  
                        else:
                              return render_template('Inicio.html')  
                else:
                        return render_template('login.html')
        except Exception as e:
                flash(e)
                return redirect(url_for('GenAlicuota',idReside=idReside))

@app.route('/addAlicuotas/<string:idReside>',methods=['POST'])
def addAlicuotas(idReside):
        try:
               if request.method == 'POST':
                        fecha = request.form['fecha'] 
                        fecha = fecha.replace("-","")
                        sql = "select detCodPresupuesto, codPresupuesto, codEtapa, (select nombreetapa from etapas where idetapas = codetapa) as nombreetapa,codResidencia, gastoTotal, gastoEtapa, gastoComunal, nroRecidencia, metrosCuadrados, nroResidenciaEtapa, metrosCuadradosEtapa,alicuotaSelecionada, "
                        sql = sql + " case alicuotaSelecionada  when 'var' then 'Valor Alicuota por Residencia'  when 'vamc' then 'Valor Alicuota por metro cuadrado'  when 'vare' then 'Valor Alicuota por Residencia y por Etapa' when 'vamce' then 'Valor Alicuota por metro cuadrado y Etapa' end as AlicuotaPor,"
                        sql = sql + " valorAlicuota,necesidades from detpresupuesto where codpresupuesto in (select codpresupuesto from presupuesto where codresidencia = %s and estado = 'Activo')"
                        presupuestos = consTablaPara(sql,[idReside])
                        propiedades = consTablaPara("select idPropiedad, idEtapas, idResidencia, TipoPropiedad, Nropropiedad, metrosCuadrados, Nombre from propiedad where idresidencia = %s and Estado = 'Activo' order by idEtapas",[idReside])
                        for propiedad in propiedades:
                                for presupuesto in presupuestos:
                                        if propiedad[1] == presupuesto[2]:
                                                if presupuesto[12] == "vamce":  
                                                        valorAli = presupuesto[14] * propiedad[5]                                                        
                                                        consInsTabla("INSERT INTO ingreso (CodRecidencia, CodEtapa, CodPropiedad, CodPersona, codPresupuesto,fecha, valor, Tipo, Estado, descripcion, usuarioMod, fechaMod, HoraMod,fechaing) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[idReside,propiedad[1],propiedad[0],0,presupuesto[1],fecha,valorAli, 1,'Pendiente','Ingreso Por Alicuota ' + fecha[:6] ,session['idUsuSisfiab'],g.fechaNum,time.strftime("%H:%M:%S"),g.fechaNum])
                                                if presupuesto[12] == "vamc":
                                                        valorAli = presupuesto[14] * propiedad[5]                                                        
                                                        consInsTabla("INSERT INTO ingreso (CodRecidencia, CodEtapa, CodPropiedad, CodPersona, codPresupuesto,fecha, valor, Tipo, Estado, descripcion, usuarioMod, fechaMod, HoraMod,fechaing) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[idReside,propiedad[1],propiedad[0],0,presupuesto[1],fecha,valorAli, 1,'Pendiente','Ingreso Por Alicuota ' + fecha[:6] ,session['idUsuSisfiab'],g.fechaNum,time.strftime("%H:%M:%S"),g.fechaNum])
                                                if presupuesto[12] == "vare":
                                                        valorAli = presupuesto[14]                                                         
                                                        consInsTabla("INSERT INTO ingreso (CodRecidencia, CodEtapa, CodPropiedad, CodPersona, codPresupuesto,fecha, valor, Tipo, Estado, descripcion, usuarioMod, fechaMod, HoraMod,fechaing) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[idReside,propiedad[1],propiedad[0],0,presupuesto[1],fecha,valorAli, 1,'Pendiente','Ingreso Por Alicuota ' + fecha[:6] ,session['idUsuSisfiab'],g.fechaNum,time.strftime("%H:%M:%S"),g.fechaNum])
                                                if presupuesto[12] == "var":
                                                        valorAli = presupuesto[14]                                                         
                                                        consInsTabla("INSERT INTO ingreso (CodRecidencia, CodEtapa, CodPropiedad, CodPersona, codPresupuesto,fecha, valor, Tipo, Estado, descripcion, usuarioMod, fechaMod, HoraMod,fechaing) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[idReside,propiedad[1],propiedad[0],0,presupuesto[1],fecha,valorAli, 1,'Pendiente','Ingreso Por Alicuota ' + fecha[:6] ,session['idUsuSisfiab'],g.fechaNum,time.strftime("%H:%M:%S"),g.fechaNum])

                                                break

                        return redirect(url_for('Ingresos',idReside=idReside))  
        except Exception as e:
                flash(e)
                return redirect(url_for('GenAlicuota',idReside=idReside))

@app.route('/GenIngresos/<string:idReside>')
def GenIngresos(idReside):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) >= 3 and int(g.CodCondominio) == int(idReside)):
                                residencia = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo from condominio where estado = "Activo" and idCondominio = %s',[idReside]) 
                                tipo = consTabla("select codigo,valor from parametros where CodDefinicion  ='TipoIngreso' and estado = 'Activo'")                                                              
                                multas = consTablaPara('select CodMulta, Descripcion, valor, porcentaje from multas where CodResidencia = %s and estado = "Activo"',[idReside])                  
                                propiedades = consTablaPara('select idPropiedad, idEtapas, TipoPropiedad,(select valor from parametros where CodDefinicion  ="TipoPropiedad" and codigo = TipoPropiedad) as tipo, Nropropiedad, Nombre from propiedad where idResidencia = %s and Estado = "Activo"',[idReside])
                                return render_template("/Administrador/GenIngreso.html",residencia=residencia,tiposIngresos=tipo,multas=multas,propiedades=propiedades)  
                        else:
                              return render_template('Inicio.html')  
                else:
                        return render_template('login.html')
        except Exception as e:
                flash(e)
                return redirect(url_for('GenAlicuota',idReside=idReside))

@app.route('/addIngresos/<string:idReside>',methods=['POST'])
def addIngresos(idReside):
        try:
               if request.method == 'POST':
                        tipo = request.form['tipo'] 
                        subDefFinal = 0
                        if tipo == "3":
                                Subtipo = request.form['Subtipo']
                                subDef = Subtipo.split()
                                subDefFinal = subDef[0]

                        propiDef = 0
                        propiEta = 0
                        
                        if tipo == "2" or tipo == "3":
                                propiedad = request.form['propiedad'] 
                                propi = propiedad.split()
                                propiDef = propi[0]
                                propiEta = propi[2]
                        descripcion = request.form['descripcion'] 
                        valor = request.form['valor']
                        fecha = request.form['fecha'] 
                        fecha = fecha.replace("-","")                                            
                        consInsTabla("INSERT INTO ingreso (CodRecidencia, CodEtapa, CodPropiedad, CodPersona, codPresupuesto,fecha, valor, Tipo, Estado, descripcion, usuarioMod, fechaMod, HoraMod,fechaing,SubTipo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[idReside,propiEta,propiDef,0,0,fecha,valor, tipo,'Pendiente',descripcion ,session['idUsuSisfiab'],g.fechaNum,time.strftime("%H:%M:%S"),g.fechaNum,subDefFinal])

                        return redirect(url_for('Ingresos',idReside=idReside))  
        except Exception as e:
                flash(e)
                return redirect(url_for('GenAlicuota',idReside=idReside))

#cobros
@app.route('/Cobros/<string:idReside>/<string:idPropiedad>')
def Cobros(idReside,idPropiedad):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) >= 3 and int(g.CodCondominio) == int(idReside)):
                                residencia = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo from condominio where estado = "Activo" and idCondominio = %s',[idReside])        
                                sql = "select CodIngreso, CodRecidencia, CodEtapa, CodPropiedad, CodPersona, codPresupuesto, fecha, valor, Tipo,(select valor from parametros where CodDefinicion = 'TipoIngreso' and codigo =Tipo) as nombretipo, descripcion, IFNULL((select descripcion from multas where codmulta = SubTipo),'') as nombresubtipo ,SubTipo,IFNULL((select max(NroPago) from cobros where cobros.codIngreso = ingreso.codIngreso),'0') as nropago,IFNULL((select sum(valor) from cobros where cobros.codIngreso = ingreso.codIngreso),'0') as valcobrado from ingreso where estado = 'Pendiente' and codrecidencia = %s and codpropiedad = %s order by fecha"
                                ingresos = consTablaPara(sql,[idReside,idPropiedad])
                                tipoCobros = consTabla ('select codigo,valor from parametros where estado = "Activo" and CodDefinicion = "FormaCobro"')        
                                propiedad = consTablaPara("select (select valor from parametros where CodDefinicion = 'TipoPropiedad' and codigo =  TipoPropiedad)as tipovi ,Nropropiedad,nombre,idpropiedad from propiedad where idResidencia = %s and idpropiedad = %s",[idReside,idPropiedad])
                                instituciones = consTabla ('select codigo,valor from parametros where estado = "Activo" and CodDefinicion = "Instituciones"')        
                                bancos = consTablaPara('select codbanco,nombre,nrocta from bancos where codResidencia = %s and estado = "Activo" and Nombre <> "CAJA CHICA"',[idReside])
                                return render_template("/Administrador/cobros.html",residencia=residencia,ingresos=ingresos,tipoCobros=tipoCobros,propiedad=propiedad,instituciones=instituciones,bancos=bancos)  
                        else:
                                return render_template('Inicio.html')  
                else:
                        return render_template('login.html')
        except Exception as e:
                flash(e)
                return redirect(url_for('cobros',idReside=idReside,idPropiedad=idPropiedad))

@app.route('/addCobros/<string:idReside>/<string:idpropiedad>',methods=['POST'])
def addCobros(idReside,idpropiedad):
        try:
               if request.method == 'POST':
                        
                        fecha = request.form['fecha'] 
                        fecha = fecha.replace("-","")  
                        tipo = request.form['tipocobro']
                        institucion = 0
                        nrodocumento = ""
                        codbanco = 0
                        nrodepositoref = ""
                        fechadep=0
                        usudeposito=0
                        horadeposito=""
                        #nro de cobro
                        nrocobro= consTablaPara("select IFNULL(max(NroCobro),0) + 1 from cobros where codResidencia = %s",[idReside])
                        #nro de deposito
                        nrodeposito=0
                        referenciaDeposito=''
                        


                        if tipo == "2": #cheque
                                institucion = request.form['institucion']
                                nrodocumento = request.form['nrodoc']
                        if tipo == "3" : #transferencia
                                codbanco = request.form['banco']
                                nrodocumento = request.form['nrodoc']
                                nrodepositoref = request.form['nrodeposito']
                                fechadep=fecha
                                usudeposito=session['idUsuSisfiab']
                                horadeposito=time.strftime("%H:%M:%S")
                                nrodeposito = consTablaPara("select IFNULL(max(NroDeposito),0) + 1 from cobros where codResidencia = %s",[idReside])
                                referenciaDeposito = request.form['descripcion']
                        if tipo == "5" : #deposito
                                codbanco = request.form['banco']
                                nrodepositoref = request.form['nrodeposito']
                                fechadep=fecha
                                usudeposito=session['idUsuSisfiab']
                                horadeposito=time.strftime("%H:%M:%S")                                
                                nrodeposito = consTablaPara("select IFNULL(max(NroDeposito),0) + 1 from cobros where codResidencia = %s",[idReside])
                                referenciaDeposito = request.form['descripcion']

                        descripcion = request.form['descripcion'] 
                                          
                        indexDet=1

                        while request.form.get('I' + str(indexDet)):
                                saldo = float(request.form['vv'+ str(indexDet)])
                                valor = float(request.form['c'+ str(indexDet)])
                                
                                if float(valor) > 0:
                                        codingre = request.form.get('I' + str(indexDet))
                                        nropag = int(request.form.get('NP' + str(indexDet))) + 1 
                                        sql = "INSERT INTO cobros ( codIngreso, NroPago, FechaPago, FormaCobro, Institucion, nrodocumento, codBanco, UsuarioIng, fechaIng, HoraIng, UsuarioMod, fechaMod, HoraMod, FechaDepo, UsuarioDepo, HoraDepo, NroDepoRefe, Conciliado, FechaConcili, UsuarioConcilia, HoraConcilia, Estado,referencia,valor,codpropiedad,NroCobro,NroDeposito,codResidencia,referenciaDeposito,TipoCobro,ValorTotal) " 
                                        sql = sql + " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"                                        
                                        consInsTabla(sql ,[codingre,nropag,fecha,tipo,institucion,nrodocumento,codbanco,session['idUsuSisfiab'],g.fechaNum,time.strftime("%H:%M:%S"),0,0 ,'',fechadep,usudeposito,horadeposito,nrodepositoref,'NO',0,0,'','Activo',descripcion,valor,idpropiedad,nrocobro,nrodeposito,idReside,referenciaDeposito,1,valor])
                                        if float(saldo) == float(valor):
                                                consUpdTabla("UPDATE ingreso set estado='Cancelado', fechaMod=%s, usuarioMod=%s, HoraMod=%s where CodIngreso=%s",[g.fechaNum ,session['idUsuSisfiab'],time.strftime("%H:%M:%S"),codingre])
                                        

                                indexDet = indexDet + 1
                        return redirect(url_for('Ingresos',idReside=idReside))  
        except Exception as e:
                flash(e)
                return redirect(url_for('cobros',idReside=idReside,idpropiedad=idpropiedad))

# Deposito bancario o Efectivizacion
@app.route('/Depositobancario/<string:idReside>')
def Depositobancario(idReside):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) >= 3 and int(g.CodCondominio) == int(idReside)):
                                residencia = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo from condominio where estado = "Activo" and idCondominio = %s',[idReside])        
                                sql = "select nrocobro,TipoCobro,(select valor from parametros where CodDefinicion = 'FormaCobro' and codigo = FormaCobro) as cobro,Institucion,IFNULL((select valor from parametros where CodDefinicion = 'Instituciones' and codigo =Institucion),'') as Institucioncobro,nrodocumento,referencia,sum(valorTotal) as valor from cobros where codBanco = 0 and estado = 'Activo'"
                                sql += " and Formacobro in (1,2) and codResidencia = %s group by nrocobro order by nrocobro"
                                cobros = consTablaPara(sql,[idReside])
                                bancos = consTablaPara('select codbanco,nombre,nrocta from bancos where codResidencia = %s and estado = "Activo" and Nombre <> "CAJA CHICA"',[idReside])
                                return render_template("/Administrador/Depositobancario.html",residencia=residencia,bancos=bancos,cobros=cobros)  
                        else:
                                return render_template('Inicio.html')  
                else:
                        return render_template('login.html')
        except Exception as e:
                flash(e)
                return redirect(url_for('Depositobancario',idReside=idReside))

@app.route('/addDepositosBancarios/<string:idReside>',methods=['POST'])
def addDepositosBancarios(idReside):
        try:
               if request.method == 'POST':
                        
                        fechadep = request.form['fecha'] 
                        fechadep = fechadep.replace("-","")                          
                        codbanco = request.form['banco']
                        nrodepositoref = request.form['nrodeposito']
                        usudeposito=session['idUsuSisfiab']
                        horadeposito=time.strftime("%H:%M:%S")                                
                        nrodeposito = consTablaPara("select IFNULL(max(NroDeposito),0) + 1 from cobros where codResidencia = %s",[idReside])
                        referenciaDeposito = request.form['descripcion']
                                          
                        indexDet=1

                        while request.form.get('I' + str(indexDet)):                                
                                codcobro = request.form.get('I' + str(indexDet))
                                cheq = request.form.get('ch' + str(indexDet))
                                if cheq:
                                        consUpdTabla("UPDATE cobros set  fechamod=%s, UsuarioMod=%s,HoraMod=%s,codBanco=%s,FechaDepo=%s,UsuarioDepo=%s,HoraDepo=%s,NroDepoRefe=%s,NroDeposito=%s,referenciaDeposito=%s where NroCobro=%s and codResidencia = %s",[g.fechaNum ,usudeposito,horadeposito,codbanco,fechadep,usudeposito,horadeposito,nrodepositoref,nrodeposito,referenciaDeposito,codcobro,idReside])                                  
                                indexDet = indexDet + 1

                        return redirect(url_for('Ingresos',idReside=idReside))  
        except Exception as e:
                flash(e)
                return redirect(url_for('Depositobancario',idReside=idReside))

# ingresos caja chica
@app.route('/CajaChica/<string:idReside>')
def CajaChica(idReside):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) >= 3 and int(g.CodCondominio) == int(idReside)):
                                residencia = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo from condominio where estado = "Activo" and idCondominio = %s',[idReside])        
                                sql = "select nrocobro,TipoCobro,(select valor from parametros where CodDefinicion = 'FormaCobro' and codigo = FormaCobro) as cobro,referencia,sum(valorTotal) as valorTotal from cobros where codBanco = 0 and estado = 'Activo'"
                                sql += " and Formacobro = 1 and codResidencia = %s group by nrocobro order by nrocobro"
                                cobros = consTablaPara(sql,[idReside])
                                bancos = consTablaPara('select codbanco,nombre,nrocta from bancos where codResidencia = %s and estado = "Activo" and Nombre = "CAJA CHICA"',[idReside])
                                return render_template("/Administrador/Cajachica.html",residencia=residencia,bancos=bancos,cobros=cobros)  
                        else:
                                return render_template('Inicio.html')  
                else:
                        return render_template('login.html')
        except Exception as e:
                flash(e)
                return redirect(url_for('CajaChica',idReside=idReside))

@app.route('/addcajachica/<string:idReside>',methods=['POST'])
def addcajachica(idReside):
        try:
               if request.method == 'POST':
                        
                        fechadep = request.form['fecha'] 
                        fechadep = fechadep.replace("-","")                          
                        codbanco = request.form['banco']
                        nrodepositoref = "9999999999"
                        usudeposito=session['idUsuSisfiab']
                        horadeposito=time.strftime("%H:%M:%S")                                
                        nrodeposito = consTablaPara("select IFNULL(max(NroDeposito),0) + 1 from cobros where codResidencia = %s",[idReside])
                        referenciaDeposito = request.form['descripcion']
                                          
                        indexDet=1

                        while request.form.get('I' + str(indexDet)):                                
                                codcobro = request.form.get('I' + str(indexDet))
                                cheq = request.form.get('ch' + str(indexDet))
                                if cheq:
                                        consUpdTabla("UPDATE cobros set  fechamod=%s, UsuarioMod=%s,HoraMod=%s,codBanco=%s,FechaDepo=%s,UsuarioDepo=%s,HoraDepo=%s,NroDepoRefe=%s,NroDeposito=%s,referenciaDeposito=%s where NroCobro=%s and codResidencia = %s",[g.fechaNum ,usudeposito,horadeposito,codbanco,fechadep,usudeposito,horadeposito,nrodepositoref,nrodeposito,referenciaDeposito,codcobro,idReside])                                  
                                indexDet = indexDet + 1

                        return redirect(url_for('Ingresos',idReside=idReside))  
        except Exception as e:
                flash(e)
                return redirect(url_for('CajaChica',idReside=idReside))

#Abonos
@app.route('/Abono/<string:idReside>/<string:idPropiedad>')
def Abono(idReside,idPropiedad):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) >= 3 and int(g.CodCondominio) == int(idReside)):
                                residencia = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo from condominio where estado = "Activo" and idCondominio = %s',[idReside])        
                                tipoCobros = consTabla ('select codigo,valor from parametros where estado = "Activo" and CodDefinicion = "FormaCobro"')        
                                propiedad = consTablaPara("select (select valor from parametros where CodDefinicion = 'TipoPropiedad' and codigo =  TipoPropiedad)as tipovi ,Nropropiedad,nombre,idpropiedad from propiedad where idResidencia = %s and idpropiedad = %s",[idReside,idPropiedad])
                                instituciones = consTabla ('select codigo,valor from parametros where estado = "Activo" and CodDefinicion = "Instituciones"')        
                                bancos = consTablaPara('select codbanco,nombre,nrocta from bancos where codResidencia = %s and estado = "Activo" and Nombre <> "CAJA CHICA"',[idReside])
                                sql = "select codCobro, FechaPago, FormaCobro,(select valor from parametros where CodDefinicion = 'FormaCobro' and codigo = FormaCobro) as Nomformacobro,Institucion, IFNULL((select valor from parametros where CodDefinicion = 'Instituciones' and codigo =Institucion),'') as Institucioncobro,"
                                sql += " nrodocumento, referencia,(select sum(valor) from cobros as b where b.codResidencia = a.codResidencia and b.codpropiedad = a.codpropiedad and b.nrocobro = a.nrocobro) as valor " 
                                sql += ", codpropiedad, NroCobro, codResidencia, ValorTotal from cobros as a where estado = 'Activo' and codResidencia = %s and tipoCobro = 2 and codpropiedad =%s and valor = 0"
                                cobrosAbonos = consTablaPara(sql,[idReside,idPropiedad])
                                sql = "select CodIngreso, CodRecidencia, CodEtapa, CodPropiedad, CodPersona, codPresupuesto, fecha, valor, Tipo,(select valor from parametros where CodDefinicion = 'TipoIngreso' and codigo =Tipo) as nombretipo, descripcion, IFNULL((select descripcion from multas where codmulta = SubTipo),'') as nombresubtipo ,SubTipo,IFNULL((select max(NroPago) from cobros where cobros.codIngreso = ingreso.codIngreso),'0') as nropago,IFNULL((select sum(valor) from cobros where cobros.codIngreso = ingreso.codIngreso),'0') as valcobrado from ingreso where estado = 'Pendiente' and codrecidencia = %s and codpropiedad = %s order by fecha"
                                ingresos = consTablaPara(sql,[idReside,idPropiedad])
                                valcobro = 0
                                for ingreso in ingresos:
                                        valcobro = valcobro + float(ingreso[7]) - float(ingreso[14])
                                valabonos = 0
                                for cobrosAbono in cobrosAbonos:
                                        valabonos = valabonos + float(cobrosAbono[12]) - float(cobrosAbono[8])

                                return render_template("/Administrador/Abono.html",residencia=residencia,tipoCobros=tipoCobros,propiedad=propiedad,instituciones=instituciones,bancos=bancos,cobrosAbonos=cobrosAbonos,ingresos=ingresos,valcobro=valcobro,valabonos=valabonos)  
                        else:
                                return render_template('Inicio.html')  
                else:
                        return render_template('login.html')
        except Exception as e:
                flash(e)
                return redirect(url_for('Abono',idReside=idReside,idPropiedad=idPropiedad))

@app.route('/addAbonos/<string:idReside>/<string:idpropiedad>',methods=['POST'])
def addAbonos(idReside,idpropiedad):
        try:
               if request.method == 'POST':
                        
                        fecha = request.form['fecha'] 
                        fecha = fecha.replace("-","")  
                        tipo = request.form['tipocobro']
                        institucion = 0
                        nrodocumento = ""
                        codbanco = 0
                        nrodepositoref = ""
                        fechadep=0
                        usudeposito=0
                        horadeposito=""
                        #nro de cobro
                        nrocobro= consTablaPara("select IFNULL(max(NroCobro),0) + 1 from cobros where codResidencia = %s",[idReside])
                        #nro de deposito
                        nrodeposito=0
                        referenciaDeposito=''
                        


                        if tipo == "2": #cheque
                                institucion = request.form['institucion']
                                nrodocumento = request.form['nrodoc']
                        if tipo == "3" : #transferencia
                                codbanco = request.form['banco']
                                nrodocumento = request.form['nrodoc']
                                nrodepositoref = request.form['nrodeposito']
                                fechadep=fecha
                                usudeposito=session['idUsuSisfiab']
                                horadeposito=time.strftime("%H:%M:%S")
                                nrodeposito = consTablaPara("select IFNULL(max(NroDeposito),0) + 1 from cobros where codResidencia = %s",[idReside])
                                referenciaDeposito = request.form['descripcion']
                        if tipo == "5" : #deposito
                                codbanco = request.form['banco']
                                nrodepositoref = request.form['nrodeposito']
                                fechadep=fecha
                                usudeposito=session['idUsuSisfiab']
                                horadeposito=time.strftime("%H:%M:%S")                                
                                nrodeposito = consTablaPara("select IFNULL(max(NroDeposito),0) + 1 from cobros where codResidencia = %s",[idReside])
                                referenciaDeposito = request.form['descripcion']

                        descripcion = request.form['descripcion'] 
                                          

                        valor =  request.form['valor']
                                
                        sql = "INSERT INTO cobros ( codIngreso, NroPago, FechaPago, FormaCobro, Institucion, nrodocumento, codBanco, UsuarioIng, fechaIng, HoraIng, UsuarioMod, fechaMod, HoraMod, FechaDepo, UsuarioDepo, HoraDepo, NroDepoRefe, Conciliado, FechaConcili, UsuarioConcilia, HoraConcilia, Estado,referencia,valor,codpropiedad,NroCobro,NroDeposito,codResidencia,referenciaDeposito,TipoCobro,ValorTotal) " 
                        sql = sql + " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"                                        
                        consInsTabla(sql ,[0,0,fecha,tipo,institucion,nrodocumento,codbanco,session['idUsuSisfiab'],g.fechaNum,time.strftime("%H:%M:%S"),0,0 ,'',fechadep,usudeposito,horadeposito,nrodepositoref,'NO',0,0,'','Activo',descripcion,0,idpropiedad,nrocobro,nrodeposito,idReside,referenciaDeposito,2,valor])
                                        
                        return redirect(url_for('Abono',idReside=idReside,idPropiedad=idpropiedad))  
        except Exception as e:
                flash(e)
                return redirect(url_for('Abono',idReside=idReside,idpropiedad=idpropiedad))

@app.route('/cruceAbonos/<string:idReside>/<string:idpropiedad>',methods=['POST'])
def cruceAbonos(idReside,idpropiedad):
        try:
               if request.method == 'POST':    
                        vATotal =  float(request.form['vATotal'])
                        vITotal =  float(request.form['vITotal'])
                        indexDetAbono=1
                        lista = []
                        listaPendiente=[]
                        while request.form.get('nc' + str(indexDetAbono)):                                                                                                                                                   
                                indexDet=1
                                codcobro = request.form['c'+ str(indexDetAbono)]
                                numcobro = request.form['nc'+ str(indexDetAbono)]
                                vAbono = float(request.form['vAbono'+ str(indexDetAbono)])                                 
                                while request.form.get('I' + str(indexDet)):
                                        
                                        if vATotal > 0:                                                
                                                codingreso = request.form['I'+ str(indexDet)]
                                                                                      
                                                if codingreso not in lista:
                                                        
                                                        vcobroIngreso = float(request.form['vcobro'+ str(indexDet)])                                                                                                
                                                        nropago1 = consTablaPara("(select max(NroPago) from cobros where cobros.codIngreso = %s)",[codingreso]) 
                                                        print(nropago1)
                                                        if nropago1[0][0] == None:
                                                                nropago = 1
                                                        else:
                                                                nropago = int(nropago1[0][0]) + 1                                                   
                                                        usuariosis = session['idUsuSisfiab']
                                                        fechasis = g.fechaNum
                                                        horasis = time.strftime("%H:%M:%S")  
                                                        for elemento in listaPendiente:
                                                                elemLista = []
                                                                elemLista = elemento
                                                                if codingreso in elemLista:
                                                                        vcobroIngreso = float(elemLista[1])
                                                                        listaPendiente=[]

                                                        if float(vAbono) < float(vcobroIngreso):
                                                                print(1)
                                                                listaPendiente.append([codingreso, float (vcobroIngreso) - float(vAbono)])
                                                                consUpdTabla('UPDATE cobros set fechaCruceAbono = %s,UsuarioCruceAbono=%s,valor = %s,UsuarioMod=%s,fechaMod=%s,HoraMod=%s,codIngreso=%s,NroPago=%s where codCobro=%s',[fechasis,usuariosis,vAbono,usuariosis,fechasis,horasis,codingreso,nropago,codcobro])
                                                                vATotal = vATotal - vAbono
                                                                vAbono = vAbono - vAbono
                                                                print(listaPendiente)
                                                                break
                                                        if float(vAbono) == float(vcobroIngreso):
                                                                print(2)
                                                                lista.append(codingreso)
                                                                consUpdTabla('UPDATE cobros set fechaCruceAbono = %s,UsuarioCruceAbono=%s,valor = %s,UsuarioMod=%s,fechaMod=%s,HoraMod=%s,codIngreso=%s,NroPago=%s where codCobro=%s',[fechasis,usuariosis,vAbono,usuariosis,fechasis,horasis,codingreso,nropago,codcobro])
                                                                consUpdTabla("UPDATE ingreso set estado='Cancelado', fechaMod=%s, usuarioMod=%s, HoraMod=%s where CodIngreso=%s",[g.fechaNum ,session['idUsuSisfiab'],time.strftime("%H:%M:%S"),codingreso])
                                                                vAbono = vAbono - vcobroIngreso
                                                                vATotal = vATotal - vcobroIngreso
                                                        if float(vAbono) > float(vcobroIngreso):
                                                                print(3)
                                                                sql = "insert into cobros ( codIngreso, NroPago, FechaPago, FormaCobro, Institucion, nrodocumento, codBanco, UsuarioIng, fechaIng, HoraIng, UsuarioMod, fechaMod, HoraMod, FechaDepo, UsuarioDepo, HoraDepo, NroDepoRefe, Conciliado, FechaConcili, UsuarioConcilia, HoraConcilia, Estado, referencia, valor, codpropiedad, NroCobro, NroDeposito, codResidencia, referenciaDeposito, TipoCobro, ValorTotal, fechaCruceAbono, UsuarioCruceAbono) select  codIngreso, NroPago, FechaPago, FormaCobro, Institucion, nrodocumento, codBanco, UsuarioIng, fechaIng, HoraIng, UsuarioMod, fechaMod, HoraMod, FechaDepo, UsuarioDepo, HoraDepo, NroDepoRefe, Conciliado, FechaConcili, UsuarioConcilia, HoraConcilia, Estado, referencia, valor, codpropiedad, NroCobro, NroDeposito, codResidencia, referenciaDeposito, TipoCobro, ValorTotal, fechaCruceAbono, UsuarioCruceAbono from cobros where codCobro = %s"
                                                                consInsTabla(sql,[codcobro])
                                                                consUpdTabla('UPDATE cobros set fechaCruceAbono = %s,UsuarioCruceAbono=%s,valor = %s,UsuarioMod=%s,fechaMod=%s,HoraMod=%s,codIngreso=%s,NroPago=%s where codCobro=%s',[fechasis,usuariosis,vcobroIngreso,usuariosis,fechasis,horasis,codingreso,nropago,codcobro])
                                                                consUpdTabla("UPDATE ingreso set estado='Cancelado', fechaMod=%s, usuarioMod=%s, HoraMod=%s where CodIngreso=%s",[g.fechaNum ,session['idUsuSisfiab'],time.strftime("%H:%M:%S"),codingreso])
                                                                codcobro = consTablaPara("select codcobro from cobros where codResidencia = %s and codpropiedad = %s and valorTotal = %s and valor = 0 and NroCobro = %s",[idReside,idpropiedad,vAbono,numcobro])
                                                                lista.append(codingreso)
                                                                vATotal = vATotal - vcobroIngreso
                                                                vAbono = vAbono - vcobroIngreso
                                        indexDet= indexDet + 1
                                indexDetAbono = indexDetAbono + 1
                        return redirect(url_for('Abono',idReside=idReside,idPropiedad=idpropiedad))  
        except Exception as e:
                flash(e)
                return redirect(url_for('Abono',idReside=idReside,idpropiedad=idpropiedad))


#IngreSinIdenti
