import arcpy
import os

arcpy.env.overwriteOutput = True


ws = arcpy.GetParameterAsText(0)
fc = arcpy.GetParameterAsText(1)
codi = arcpy.GetParameterAsText(2)
descripcion = arcpy.GetParameterAsText(3)

fallasCategorias = ['Falla', 'Falla normal', 'Falla inversa', 'Falla de rumbo', 'Eje anticlinal', 'Eje sinclinal', 'Eje anticlinal volcado', 'Eje sinclinal volcado']


def consistencia_01_descripcion(fc=fc, descripcion=descripcion):
	arcpy.AddMessage(" Evaluando el campo DESCRIPCION: {}...".format(descripcion))
	informacion = []
	errores = [[1, x[0], x[1]] for x in arcpy.da.SearchCursor(fc, ["OID@", descripcion]) if x[1] not in fallasCategorias]
	if len(errores) != 0:
		informacion.extend(errores)
	else:
		pass
	return informacion



def main(fc=fc, ws=ws, codi=codi, descripcion=descripcion):
	informacion = []
	arcpy.AddMessage("\n Evaluando la existencia de la GeodataBase: {}... ".format(ws))
	try:
		desc = arcpy.Describe(ws)
		if desc.datatype == u'Workspace':
			if arcpy.Exists(os.path.join(ws, 'FD1_INSUMOS', 'PM_V3_FallasGeologicas')):
				cons01 = consistencia_01_descripcion()
				if len(cons01) > 0:
					informacion.extend(cons01)
					arcpy.AddMessage("  Errores:")
					for x in informacion:
						arcpy.AddWarning("   FID: {} | CAMPO: DESCRIPCION | Descripcion: El valor ingresado '{}' no es correcto...".format(x[1], x[2]))
				else:
					arcpy.AddMessage(" Realizando la carga de informacion...")
					copia = arcpy.CopyFeatures_management(fc, "in_memory\\fallasGeologicas")
					campos = {"CODI": codi, "DESCRIPCION": descripcion}
					arcpy.DeleteRows_management(os.path.join(ws, 'FD1_INSUMOS', 'PM_V3_FallasGeologicas'))
					for k, v in campos.items():
						arcpy.AlterField_management(copia, v, k)
					arcpy.Append_management(copia, os.path.join(ws, 'FD1_INSUMOS', 'PM_V3_FallasGeologicas'), "NO_TEST")
					arcpy.SetParameterAsText(4, os.path.join(ws, 'FD1_INSUMOS', 'PM_V3_FallasGeologicas'))
					arcpy.AddMessage(" La carga de informacion concluyo correctamente... \n")
			else:
				arcpy.AddWarning(" El espacio de trabajo agregado no es correcto o el feature class PM_V3_FallasGeologicas no existe... \n")
		else:
			arcpy.AddWarning(" El espacio de trabajo agregado no es el correcto... \n")
	except Exception as e:
		arcpy.AddWarning("\n"+ " " + e.message + "\n")
	arcpy.AddMessage(" Proceso finalizado \n")


if __name__ == "__main__":
	main()