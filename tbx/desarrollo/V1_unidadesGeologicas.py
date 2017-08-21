import arcpy
import os


arcpy.env.overwriteOutput = True


ws = arcpy.GetParameterAsText(0)
fc = arcpy.GetParameterAsText(1)
codi = arcpy.GetParameterAsText(2)
grado = arcpy.GetParameterAsText(3)
valor = arcpy.GetParameterAsText(4)
condicion = arcpy.GetParameterAsText(5)


parametros = arcpy.GetParameterInfo()


def consistencia_01_Grado(fc=fc, grado=grado):
	arcpy.AddMessage(" Evaluando el campo GRADO: {}...".format(grado))
	informacion = []
	errores = [[1, x[0], x[1]] for x in arcpy.da.SearchCursor(fc, ["OID@", grado]) if x[1] not in ['Muy alto', 'Alto', 'Medio', 'Bajo', 'Muy bajo']]
	if len(errores) != 0:
		informacion.extend(errores)
	else:
		pass
	return informacion



def consistencia_02_Valor(fc=fc, valor=valor):
	arcpy.AddMessage(" Evaluando el campo VALOR: {}...".format(valor))
	informacion = []
	errores = [[2, x[0], x[1]] for x in arcpy.da.SearchCursor(fc, ["OID@", valor]) if x[1] < 1.2 and x[1] > 3.0]
	if len(errores) != 0:
		informacion.extend(errores)
	else:
		pass
	return informacion



def consistencia_03_Condicion(fc=fc, condicion=condicion):
	arcpy.AddMessage(" Evaluando el campo CONDICION: {}...".format(condicion))
	informacion = []
	errores = [[3, x[0], x[1]] for x in arcpy.da.SearchCursor(fc, ["OID@", condicion]) if x[1] not in ['Metalotecto', 'No metalotecto']]
	if len(errores) != 0:
		informacion.extend(errores)
	else:
		pass
	return informacion



def consistencia_04_Nulos(fc=fc, parametros=parametros):
	informacion = []
	for x in parametros[2:6]:
		for m in arcpy.da.SearchCursor(fc, [x.valueAsText]):
			if m[0] == None:
				informacion.append([4, x.valueAsText])
				break
			else:
				pass
	return informacion



def main(fc=fc, ws=ws, codi=codi, grado=grado, valor=valor, condicion=condicion):
	informacion = []
	arcpy.AddMessage("\n Evaluando la existencia de la GeodataBase: {}... ".format(ws))
	try:
		desc = arcpy.Describe(ws)
		if desc.datatype == u'Workspace':
			if arcpy.Exists(os.path.join(ws, 'FD1_INSUMOS', 'PM_V1_UnidadesGeologicas')):
				cons01 = consistencia_01_Grado()
				cons02 = consistencia_02_Valor()
				cons03 = consistencia_03_Condicion()
				cons04 = consistencia_04_Nulos()
				if len(cons01) > 0 or len(cons02) > 0 or len(cons03) > 0 or len(cons04) > 0:
					informacion.extend(cons01)
					informacion.extend(cons02)
					informacion.extend(cons03)
					informacion.extend(cons04)
					arcpy.AddMessage("   Errores:")
					for x in informacion:
						if x[0] == 1:
							arcpy.AddWarning("	FID: {} | CAMPO: GRADO | Descripcion: El valor ingresado'{}' no es correcto...".format(x[1], x[2]))
						elif x[0] == 2:
							arcpy.AddWarning("	FID: {} | CAMPO: VALOR |  Descripcion: El valor ingresado '{}' no es correcto...".format(x[1], x[2]))
						elif x[0] == 3:
							arcpy.AddWarning("	FID: {} | CAMPO: CONDICION | Descripcion: El valor ingresado '{}' no es correcto...".format(x[1], x[2]))
						elif x[0] == 4:
							arcpy.AddWarning("	CAMPO: {} | Descripcion: Contiene valores nulos".format(x[1]))
				else:
					arcpy.AddMessage(" Realizando la carga de informacion...")
					copia = arcpy.CopyFeatures_management(fc, "in_memory\\unidadesGeologicas")
					campos = {"CODI": codi, "GRADO": grado, "VALOR": valor, "CONDICION": condicion}
					arcpy.DeleteRows_management(os.path.join(ws, 'FD1_INSUMOS', 'PM_V1_UnidadesGeologicas'))
					for k, v in campos.items():
						arcpy.AlterField_management(copia, v, k)
					arcpy.Append_management(copia, os.path.join(ws, 'FD1_INSUMOS', 'PM_V1_UnidadesGeologicas'), "NO_TEST")
					arcpy.SetParameterAsText(6, os.path.join(ws, 'FD1_INSUMOS', 'PM_V1_UnidadesGeologicas'))
					arcpy.AddMessage("\n La carga de informacion concluyo correctamente... \n")
			else:
				arcpy.AddWarning("\n El espacio de trabajo agregado no es correcto o el feature class PM_V1_UnidadesGeologicas no existe... \n")
		else:
			arcpy.AddWarning("\n El espacio de trabajo agregado no es el correcto... \n")
	except Exception as e:
		arcpy.AddWarning("\n"+ " " + e.message + "\n")
	arcpy.AddMessage(" Proceso finalizado \n")


if __name__ == "__main__":
	main()