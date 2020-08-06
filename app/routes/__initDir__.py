from flask import render_template, request, json, redirect, url_for, flash, session,escape, send_from_directory,g,abort
# from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash #encryptar
import requests
import sys # captura errores
import os #ruta absoluta para subir archivos 
from app import app
from app.routes.__initDb__ import *

#presupuesto
@app.route('/MantPresupuesto')
def MantPresupuesto():
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5:
                                data = consTabla('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo,estado,fechamod,usuariomod,fechaing,(select count(*) from etapas where estado = "Activo" and etapas.idcondominio = condominio.idcondominio) as Etapas from condominio where estado = "Activo"')
                                return render_template("/Directorio/MantPresupuesto.html",condominios=data)
                        else:
                                if int(g.TipoUsuSisfiab) == 4:
                                        return redirect(url_for('Presupuesto',idReside=g.CodCondominio))
                                else:   
                                        return render_template('home.html')
                else:
                        return render_template('login.html')      
        except Exception as e:
                flash(e)
                return render_template('/Directorio/MantPresupuesto.html')


@app.route('/Presupuesto/<string:idReside>')
def Presupuesto(idReside):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) == 4 and int(g.CodCondominio) == int(idReside)):
                                data = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo from condominio where estado = "Activo" and idCondominio = %s',[idReside])        
                                sql = "select codPresupuesto, fechaInicia, fechaFin, codAsamblea, estado from presupuesto where  CodResidencia = %s order by fechaInicia"
                                presupuesto = consTablaPara(sql,[idReside])
                                return render_template("/Directorio/Presupuesto.html",condominio=data,presupuestos=presupuesto)
                        else:
                                return render_template('home.html')
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Directorio/MantPresupuesto.html')


@app.route('/ingPresupuesto/<string:idReside>')
def ingPresupuesto(idReside):
        try:
                if g.nameSisfiab:
                        if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) == 4 and int(g.CodCondominio) == int(idReside)):
                                data = consTablaPara('select idCondominio,Ruc,Nombre,Latitud,Longitud,Telefono,Paginaweb,logo,IFNULL((select fechaInicia from presupuesto where estado = "Activo" and presupuesto.CodResidencia = idCondominio),0) as fechaPresupuesto from condominio where estado = "Activo" and idCondominio = %s',[idReside])        
                                sql = "select idNecesidad, IdEtapa,(select NombreEtapa from etapas where etapas.estado = 'activo' and idCondominio = IdResidencia and IdEtapa=idetapas) as NombreEtapa, IdResidencia, tipo,(select valor from parametros where estado = 'Activo'  and CodDefinicion = 'TipoProvision' and codigo = tipo) as tipoNece, nombre  from necesidades where estado = 'Activo' and IdResidencia = %s order by IdEtapa"
                                necesidades = consTablaPara(sql,[idReside])
                                sql = "select idEtapas, NombreEtapa, idCondominio, DescripcionEtapa,(select count(*) from propiedad where estado = 'Activo' and propiedad.idetapas = etapas.idEtapas and idresidencia = idCondominio) as recidencias,COALESCE((select sum(metrosCuadrados) from propiedad where estado = 'Activo' and propiedad.idetapas = etapas.idEtapas and idresidencia = idCondominio),0) as metroscuadrados from etapas where estado = 'activo' and nombreetapa != 'Comunal' and idCondominio  = %s order by idEtapas"
                                etapas = consTablaPara(sql,[idReside])
                                return render_template("/Directorio/IngPresupuesto.html",condominio=data,necesidades=necesidades,etapas=etapas)
                        else:
                                return render_template('home.html')
                else:
                        return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Directorio/MantPresupuesto.html')

@app.route('/addPresupuesto/<string:idReside>',methods=['POST'])
def addPresupuesto(idReside):
        try:
                if request.method == 'POST':
                        if g.nameSisfiab:
                                if int(g.TipoUsuSisfiab) == 5 or (int(g.TipoUsuSisfiab) == 4 and int(g.CodCondominio) == int(idReside)):
                                        fechaInicia = request.form['fechaInicia']
                                        fechaInicia = fechaInicia.replace("-","")
                                        consUpdTabla("Update presupuesto set fechaFin=%s, estado=%s where CodResidencia =%s and estado = 'Activo'",[fechaInicia,'NoActivo',idReside ])
                                        # Grabo la cabecera del presupuesto
                                        consInsTabla("INSERT INTO presupuesto ( fechaInicia, fechaFin, codAsamblea, estado, CodResidencia, usuarioIng, fechaIng ) VALUES (%s,%s,%s,%s,%s,%s,%s)",[fechaInicia,0,0,'Activo',idReside,session['idUsuSisfiab'],g.fechaNum ])
                                        sql = "select codPresupuesto from presupuesto where fechainicia = %s and CodResidencia =%s"
                                        codPresupuesto = consTablaPara(sql,[fechaInicia,idReside])
                                        
                                        # tableReg = request.form.to_dict(flat=False)
                                        # grabo el detalle del presupuesto

                                        indexDet=1
                                        while request.form.get('EE' + str(indexDet)):

                                                index = 1
                                                # presupuesto seleccionado
                                                valAlicuota = 0
                                                if request.form.get('fsel') == "var": #valor alicuota por residencia
                                                        valAlicuota = request.form.get('valorAlicuota')
                                                if request.form.get('fsel') == "vamc": #valor alicuota por metro cuadrado 
                                                        valAlicuota = request.form.get('valorAlicuotamc')
                                                if request.form.get('fsel') == "vare": #valor alicuota por residencia y etapa
                                                        valAlicuota = request.form.get('vAliRec' + str(indexDet))
                                                if request.form.get('fsel') == "vamce": #valor alicuota por metro cuadrado y etapa
                                                        valAlicuota = request.form.get('vAliRecMc' + str(indexDet))
                                                print(valAlicuota)
                                                necesidad = ""
                                                while request.form.get('T' + str(index)):                                                        
                                                        if request.form.get('E' + str(index)) == request.form.get('EE' + str(indexDet)):
                                                                necesidad = necesidad + "E" + request.form.get('N' + str(index)) + "-" + request.form.get('T' + str(index)) +"--"
                                                        if request.form.get('Comunal' + str(index)) == "Comunal":
                                                                 necesidad = necesidad + "C" + request.form.get('N' + str(index)) + "-" + request.form.get('T' + str(index)) +"--"
                                                        index = index + 1
                                                print(necesidad)
                                                necesidad = necesidad[:-2]
                                                # print(request.form.get('fsel'))
                                                # print(valAlicuota)
                                                # print(request.form.get('nrometros') + " - " + request.form.get('nroRecide') + " - " +  request.form.get('TG') + " - " +  request.form.get('EE' + str(indexDet)) + "-" + str(idReside) + "-" + request.form.get('nRE' + str(indexDet)) + "-" + request.form.get('nmcE' + str(indexDet))+ "-" + request.form.get('gE' + str(indexDet))+ "-" + request.form.get('gC' + str(indexDet)))                                                
                                                consInsTabla("INSERT INTO detpresupuesto (codPresupuesto, codEtapa, codResidencia, gastoTotal, gastoEtapa, gastoComunal, nroRecidencia, metrosCuadrados, nroResidenciaEtapa, metrosCuadradosEtapa, alicuotaSelecionada, valorAlicuota,necesidades) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",[codPresupuesto,request.form.get('EE' + str(indexDet)),str(idReside),request.form.get('TG'),request.form.get('gE' + str(indexDet)),request.form.get('gC' + str(indexDet)),request.form.get('nroRecide'),request.form.get('nrometros'),request.form.get('nRE' + str(indexDet)),request.form.get('nmcE' + str(indexDet)),request.form.get('fsel'),valAlicuota,necesidad])
                                                indexDet = indexDet + 1

                                        
                                        return redirect(url_for('Presupuesto',idReside=idReside))
                                        # return render_template("/Directorio/IngPresupuesto.html",condominio=data,necesidades=necesidades,etapas=etapas)
                                else:
                                        return render_template('home.html')
                        else:
                                return render_template('login.html')       
        except Exception as e:
                flash(e)
                return render_template('/Directorio/MantPresupuesto.html')

