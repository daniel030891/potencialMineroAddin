import arcpy
import os


ws = arcpy.GetParameterAsText(0)
fc = arcpy.GetParameterAsText(1)
grado = arcpy.GetParameterAsText(2)
valor = arcpy.GetParameterAsText(3)



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




def main(fc=fc, ws=ws, grado=grado, valor=valor):
	informacion = []
	arcpy.AddMessage("\n Evaluando la existencia de la GeodataBase: {}... ".format(ws))
	try:
		desc = arcpy.Describe(ws)
		if desc.datatype == u'Workspace':
			if arcpy.Exists(os.path.join(ws, 'FD1_INSUMOS', 'PM_V4_DepositosMinerales')):
				cons01 = consistencia_01_Grado()
				cons02 = consistencia_02_Valor()
				if len(cons01) > 0 or len(cons02) > 0:
					informacion.extend(cons01)
					informacion.extend(cons02)
					arcpy.AddMessage("   Errores:")
					for x in informacion:
						if x[0] == 1:
							arcpy.AddWarning("	FID: {} | CAMPO: GRADO | Descripcion: El valor ingresado'{}' no es correcto...".format(x[1], x[2]))
						elif x[0] == 2:
							arcpy.AddWarning("	FID: {} | CAMPO: VALOR |  Descripcion: El valor ingresado '{}' no es correcto...".format(x[1], x[2]))
				else:
					arcpy.AddMessage(" Realizando la carga de informacion...")
					copia = arcpy.CopyFeatures_management(fc, "in_memory\\depositosMinerales")
					campos = {"GRADO": grado, "VALOR": valor}
					arcpy.DeleteRows_management(os.path.join(ws, 'FD1_INSUMOS', 'PM_V4_DepositosMinerales'))
					for k, v in campos.items():
						arcpy.AlterField_management(copia, v, k)
					arcpy.Append_management(copia, os.path.join(ws, 'FD1_INSUMOS', 'PM_V4_DepositosMinerales'), "NO_TEST")
					arcpy.SetParameterAsText(4, os.path.join(ws, 'FD1_INSUMOS', 'PM_V4_DepositosMinerales'))
					arcpy.AddMessage("\n La carga de informacion concluyo correctamente... \n")
			else:
				arcpy.AddWarning("\n El espacio de trabajo agregado no es correcto o el feature class PM_V4_DepositosMinerales no existe... \n")
		else:
			arcpy.AddWarning("\n El espacio de trabajo agregado no es el correcto... \n")
	except Exception as e:
		arcpy.AddWarning("\n"+ " " + e.message + "\n")
	arcpy.AddMessage(" Proceso finalizado \n")


if __name__ == "__main__":
	main()