# -*- coding: utf-8 -*-

# Institucion: INGEMMET  |||||||||||||||||||||||||
# Oficina: Oficina de Sistemas de Informacion  |||
# Complemento: Potencial Minero  |||||||||||||||||
# Autor: Daniel Aguado Huaccharaqui  |||||||||||||
# Fecha: Julio del 2017  |||||||||||||||||||||||||



# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::             Importando Modulos            :::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


import arcpy
import os
import threading
import webbrowser
import time
import shutil



# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::           Definiendo variables            :::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::



arcpy.env.overwriteOutput = True


ws = arcpy.GetParameterAsText(0)
pixel = arcpy.GetParameterAsText(1)
exportar = arcpy.GetParameterAsText(2)
publicar = arcpy.GetParameterAsText(3)
visualizar = arcpy.GetParameterAsText(4)


limitePoligonal = os.path.join(ws, 'FD1_INSUMOS', 'PM_V0_Cuadrante') if os.path.exists(os.path.join(ws, 'FD1_INSUMOS', 'PM_V0_Cuadrante')) else os.path.join(ws, 'FD1_INSUMOS', 'PM_V0_Region')
controlador = []


sistemaReferencia = arcpy.Describe(os.path.join(ws, 'FD1_INSUMOS')).spatialReference
arcpy.env.outputCoordinateSystem = sistemaReferencia


# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::            Declarando funciones           :::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::



def V1_variableUnidadGeologica(ws=ws, controlador=controlador):
	arcpy.AddMessage(" V1: Unidades Geologicas...")
	fc_unidadesGeologicas = os.path.join(ws, 'FD1_INSUMOS', 'PM_V1_UnidadesGeologicas')
	if arcpy.GetCount_management(fc_unidadesGeologicas)[0] != u'0':
		arcpy.CopyFeatures_management(fc_unidadesGeologicas, os.path.join(ws, 'FD2_VARIABLES', 'VAR_UNID_GEOLOGI_VEC'))
		arcpy.AddMessage("   Exportando a formato Raster...")
		arcpy.PolygonToRaster_conversion(fc_unidadesGeologicas, 'VALOR', os.path.join(ws, 'VAR_UNID_GEOLOGI_RAS'), "CELL_CENTER", 'VALOR', pixel)
		controlador.append([1, 'Unidades Geologicas'])
	else:
		controlador.append([0, 'Unidades Geologicas'])




def V2_variableConcesionesMineras(ws=ws, limitePoligonal=limitePoligonal, pixel=pixel):
	arcpy.AddMessage(" V2: Concesiones Mineras...")
	fc_unidadesGeologicas = os.path.join(ws, 'FD1_INSUMOS', 'PM_V1_UnidadesGeologicas')
	fc_catastroMinero = os.path.join(ws, 'FD1_INSUMOS', 'PM_V0_CatastroMinero')
	dissolve = arcpy.Dissolve_management(fc_catastroMinero, 'in_memory\\Dissolve_CM', 'LEYENDA;NATURALEZA', '#', 'MULTI_PART', 'DISSOLVE_LINES')
	union = arcpy.Union_analysis([dissolve, fc_unidadesGeologicas], os.path.join(ws, "FD2_VARIABLES", 'VAR_CONC_MINERAS_VEC'), 'ALL', '#', 'GAPS')
	arcpy.AddMessage("   Determinando el grado y valores...")
	with arcpy.da.UpdateCursor(union, ["VALOR", "GRADO", "LEYENDA", "CONDICION"]) as cursorUC:
		for i in cursorUC:
			if i[3] != '':
				if i[2] == 'TITULADO' and i[3] == 'Metalotecto':
					i[0], i[1] = 2.9, 'Muy Alto'
				elif i[2] == '' and i[3] == 'Metalotecto':
					i[0], i[1] = 2.5, 'Alto'
				elif i[2] == 'TITULADO' and i[3] == 'No metalotecto':
					i[0], i[1] = 2.0, 'Medio'
				elif i[2] == '' and i[3] == 'No metalotecto':
					i[0], i[1] = 1.6, 'Bajo'
				cursorUC.updateRow(i)
			else:
				cursorUC.deleteRow()
	del cursorUC
	with arcpy.da.UpdateCursor(union, ["LEYENDA", "CONDICION"], "NATURALEZA = '' AND LEYENDA = ''") as cursorUC:
		for i in cursorUC:
			i[0], i[1] == '-', '-'
			cursorUC.updateRow(i)
	del cursorUC
	deleteFields = ["FID_Dissolve_CM", "FID_PM_V1_UnidadesGeologicas"]
	arcpy.DeleteField_management(union, deleteFields)
	arcpy.AddMessage("   Exportando a formato Raster...")
	arcpy.PolygonToRaster_conversion(union, 'VALOR', os.path.join(ws, 'VAR_CONC_MINERAS_RAS'), "CELL_CENTER", 'VALOR', pixel)
	controlador.append([1, 'Conseciones Mineras'])




def V3_variableFallasGeologicas(ws=ws, limitePoligonal=limitePoligonal, pixel=pixel):
	arcpy.AddMessage(" V3: Fallas Geologicas...")
	fc = os.path.join(ws, 'FD1_INSUMOS', 'PM_V3_FallasGeologicas')
	campos = [["INFLUENCIA", "SHORT", "3"], ["GRADO", "TEXT", "50"], ["VALOR", "DOUBLE", "#"]]
	if arcpy.GetCount_management(fc)[0] != u'0':

		camposActuales = [x.name for x in arcpy.ListFields(fc)]
		for i in campos:
			if i[0] in camposActuales:
				arcpy.DeleteField_management(fc, i[0])
		for i in campos:
			if i[1] == "TEXT":
				arcpy.AddField_management(fc, i[0], i[1], '#', '#', i[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
			else:
				arcpy.AddField_management(fc, i[0], i[1], i[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')

		arcpy.AddMessage("   Determinando el grado y valores...")

		with arcpy.da.UpdateCursor(fc, ["INFLUENCIA", "GRADO", "VALOR", "Shape_Length"]) as cursorUC:
			for x in cursorUC:
				if x[3] >= 50000.0:
					x[0], x[1], x[2] = 5000, "Muy Alto", 2.9
				elif x[3] >= 10000.0 and x[1] < 50000.0:
					x[0], x[1], x[2]  = 1000, "Alto", 2.5
				else:
					x[0], x[1], x[2]  = 500, "Medio", 2.0
				cursorUC.updateRow(x)
		del cursorUC

		dissolve = arcpy.Dissolve_management(fc, 'in_memory\\Dissolve_FG', 'VALOR', 'CODI FIRST;DESCRIPCION FIRST;INFLUENCIA FIRST;GRADO FIRST', 'MULTI_PART', 'DISSOLVE_LINES')
		influencia = arcpy.Buffer_analysis(dissolve, "in_memory\\influencia", 'FIRST_INFLUENCIA')
		clip = arcpy.Clip_analysis(influencia, limitePoligonal, os.path.join(ws, "FD2_VARIABLES", 'VAR_FALLAS_VEC'))
		erase = arcpy.Erase_analysis(limitePoligonal, clip, "in_memory\\erase")
		arcpy.Append_management(erase, clip, "NO_TEST")
		
		alterFields = {"FIRST_CODI": "CODI", "FIRST_DESCRIPCION": "DESCRIPCION", "FIRST_INFLUENCIA": "INFLUENCIA", "FIRST_GRADO": "GRADO", "VALOR": "VALOR"}
		for k, v in alterFields.items():
			arcpy.AlterField_management(clip, k, v)

		deleteFields = ["BUFF_DIST", "ORIG_FID"]
		arcpy.DeleteField_management(clip, deleteFields)

		with arcpy.da.UpdateCursor(clip, ["INFLUENCIA", "CODI", "DESCRIPCION", "GRADO", "VALOR"], "VALOR IS NULL") as cursorUC:
			for x in cursorUC:
				x[0], x[1], x[2], x[3], x[4] = 0, 0, "Ausencia", "Bajo", 1.6
				cursorUC.updateRow(x)
		del cursorUC

		arcpy.AddMessage("   Exportando a formato Raster...")

		arcpy.PolygonToRaster_conversion(clip, 'VALOR', os.path.join(ws, 'VAR_FALLAS_RAS'), "CELL_CENTER", 'VALOR', pixel)
		controlador.append([1, 'Fallas geologicas'])
	else:
		controlador.append([0, 'Fallas geologicas'])
		pass



def V4_variableDepositosMinerales(ws=ws):
	arcpy.AddMessage(" V4: Depositos Minerales...")
	fc = os.path.join(ws, 'FD1_INSUMOS', 'PM_V4_DepositosMinerales')
	arcpy.CopyFeatures_management(fc, os.path.join(ws, 'FD2_VARIABLES', 'VAR_DEPO_MINERAL_VEC'))
	arcpy.AddMessage("   Exportando a formato Raster...")
	arcpy.PolygonToRaster_conversion(fc, 'VALOR', os.path.join(ws, 'VAR_DEPO_MINERAL_RAS'), "CELL_CENTER", 'VALOR', pixel)



def V5_variableGeoquimica(ws=ws, controlador=controlador):
	arcpy.AddMessage(" V5: Geoquimica...")
	geoquimica = os.path.join(ws, 'VAR_GEOQUIMICA_RAS')
	if arcpy.Exists(geoquimica):
		arcpy.AddMessage("   Verificando existencia...")
		time.sleep(1)
		controlador.append([1, 'Geoquimica'])
	else:
		controlador.append([0, 'Geoquimica'])




def V6_variableSesoresRemotos(ws=ws, limitePoligonal=limitePoligonal, pixel=pixel):
	arcpy.AddMessage(" V6: Sensores Remotos...")
	fc = os.path.join(ws, 'FD1_INSUMOS', 'PM_V6_SensoresRemotos')
	fc_copy = arcpy.CopyFeatures_management(fc, "in_memory\\sensoresRemotos")
	campos = [["GRADO", "TEXT", "50"], ["VALOR", "DOUBLE", "#"]]
	for i in campos:
		if i[1] == "TEXT":
			arcpy.AddField_management(fc_copy, i[0], i[1], '#', '#', i[2], '#', 'NULLABLE', 'NON_REQUIRED', '#')
		else:
			arcpy.AddField_management(fc_copy, i[0], i[1], i[2], '#', '#', '#', 'NULLABLE', 'NON_REQUIRED', '#')

	erase = arcpy.Erase_analysis(limitePoligonal, fc_copy, "in_memory\\erase")
	arcpy.Append_management(erase, fc_copy, "NO_TEST")

	arcpy.AddMessage("   Determinando el grado y valores...")

	with arcpy.da.UpdateCursor(fc_copy, ["TIPO", "GRADO", "VALOR", "TIPO_ARC", "TIPO_OXI"], "VALOR IS NULL") as cursorUC:
		for x in cursorUC:
			if x[0] == "Arcillas - Oxidos":
				x[1], x[2] = 'Muy Alto', 2.9
			elif x[0] == "Oxidos":
				x[1], x[2] = 'Alto', 2.7
			elif x[0] == "Arcillas":
				x[1], x[2] = 'Medio', 2.5
			elif x[0] == None:
				x[0], x[1], x[2], x[3], x[4] = 'Ausencia', 'Bajo', 1.8, 'Ausencia', 'Ausencia'

			cursorUC.updateRow(x)
	del cursorUC
	sr = arcpy.CopyFeatures_management(fc_copy, os.path.join(ws, "FD2_VARIABLES", 'VAR_SENS_REMOTOS_VEC'))

	arcpy.AddMessage("   Exportando a formato Raster...")
	arcpy.PolygonToRaster_conversion(sr, 'VALOR', os.path.join(ws, 'VAR_SENS_REMOTOS_RAS'), "CELL_CENTER", 'VALOR', pixel)




# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: Determinando Potencial Minero :::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::




def calcularPotencialMinero(ws=ws):

	arcpy.AddMessage(" Determinando el Potencial Minero...")

	arcpy.env.outputCoordinateSystem = 4326

	unidadesGeologicas = os.path.join(ws, 'VAR_UNID_GEOLOGI_RAS')
	concesionesMineras = os.path.join(ws, 'VAR_CONC_MINERAS_RAS')
	fallasGeologicas = os.path.join(ws, 'VAR_FALLAS_RAS')
	depositosMinerales = os.path.join(ws, 'VAR_DEPO_MINERAL_RAS')
	geoquimica = os.path.join(ws, 'VAR_GEOQUIMICA_RAS')
	sensoresRemotos = os.path.join(ws, 'VAR_SENS_REMOTOS_RAS')

	arcpy.AddMessage("   Realizando ponderacion...")
	#arcpy.CheckOutExtension("spatial")
	potencialMinero = arcpy.sa.Raster(unidadesGeologicas)*0.481 + arcpy.sa.Raster(concesionesMineras)*0.239 + arcpy.sa.Raster(fallasGeologicas)*0.145 + arcpy.sa.Raster(depositosMinerales)*0.0069 + arcpy.sa.Raster(geoquimica)*0.038 + arcpy.sa.Raster(sensoresRemotos)*0.027
	arcpy.AddMessage("   Exportando a formato Raster...")
	potencialMinero.save(os.path.join(ws, 'POTENCIAL_MINERO_RAS'))
	#arcpy.CheckInExtension("spatial")

	arcpy.env.outputCoordinateSystem = sistemaReferencia





# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::    Iniciar exportacion de mapas    :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


def generacionMapa(exportar=exportar, ws=ws):
	if exportar:
		arcpy.AddMessage("\n Exportando resultados como MXD y PDF...")
		time.sleep(2)
		folderPdf = os.path.join(os.path.dirname(ws), 'PM_PDF')
		folderMxd = os.path.join(os.path.dirname(ws), 'PM_MXD')
		for x in [folderPdf, folderMxd]:
			if os.path.exists(x):
				shutil.rmtree(x)
			else:
				arcpy.CreateFolder_management(os.path.dirname(x), os.path.basename(x))
		
	else:
		arcpy.AddMessage("\n")




# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: Iniciar carga de datos a la BD True/False :::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::




def publicacionResultados(publicar=publicar):
	if publicar:
		arcpy.AddMessage("\n Publicando resultados finales...")
		time.sleep(2)
	else:
		arcpy.AddMessage("\n")




# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: Iniciar GEOCATMIN en el Browser True/False ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::




def estimaExtension(limitePoligonal=limitePoligonal):
	from json import loads
	info = [x[0].extent.JSON for x in arcpy.da.SearchCursor(limitePoligonal, ["SHAPE@"], None, arcpy.SpatialReference(4326))][0]
	params = loads(info)
	return params



def definiUrl(params):
	urlIngemmet = 'http://geocatmin.ingemmet.gob.pe/geocatmin/index.html?extent={},{},{},{},4326'.format(params['xmin'], params['ymin'], params['xmax'], params['ymax'])
	webbrowser.open(urlIngemmet, new=0)



def iniciarGeocatmin(params):
    t = threading.Thread(target=definiUrl, args=(params,))
    t.start()
    t.join()



def visualizacionGeocatmin(visualizar=visualizar):
	if visualizar:
		arcpy.AddMessage(" Iniciando GEOCATMIN...")
		time.sleep(2)
		params = estimaExtension()
		iniciarGeocatmin(params)
	else:
		pass


# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::  Ejecucion de procesos organizados  :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


def main():
	arcpy.AddMessage("\n Iniciando proceso para la identificacion del Potencial Minero")
	V1_variableUnidadGeologica()
	V2_variableConcesionesMineras()
	V3_variableFallasGeologicas()
	V4_variableDepositosMinerales()
	V5_variableGeoquimica()
	V6_variableSesoresRemotos()
	try:
		calcularPotencialMinero()
		generacionMapa()
		publicacionResultados()
		visualizacionGeocatmin()
		arcpy.SetParameterAsText(5, os.path.join(ws, 'POTENCIAL_MINERO_RAS'))
		arcpy.AddMessage(" \n Proceso Finalizado")
	except:
		arcpy.AddWarning(" \n La licencia 'Spatial Analyst' no esta disponible en estos momentos \n")




if __name__ == "__main__":
	main()