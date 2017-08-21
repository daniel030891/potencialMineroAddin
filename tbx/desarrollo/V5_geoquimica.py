import arcpy
import os
import arcinfo

arcpy.env.overwriteOutput = True


ws = arcpy.GetParameterAsText(0)
raster = arcpy.GetParameterAsText(1)


def main(raster=raster, ws=ws):
	informacion = []
	arcpy.AddMessage("\n Evaluando la existencia de la GeodataBase: {}... ".format(os.path.basename(ws)))
	try:
		desc = arcpy.Describe(ws)
		if desc.datatype == u'Workspace':
			arcpy.AddMessage(" Realizando la carga de informacion...")
			#arcpy.CheckOutExtension("spatial")
			geoquimica = arcpy.sa.Fill(raster)
			geoquimica.save(os.path.join(ws, 'VAR_GEOQUIMICA_RAS'))
			#arcpy.CheckInExtension("spatial")
			arcpy.SetParameterAsText(2, os.path.join(ws, 'VAR_GEOQUIMICA_RAS'))
		else:
			arcpy.AddMessage("\n El espacio de trabajo agregado no es el correcto... \n")
	except Exception as e:
		arcpy.arcpy.AddError("\n La licencia 'Spatial Analyst' no esta disponible en estos momentos \n")

	arcpy.AddMessage(" Proceso Finalizado \n")




if __name__ == "__main__":
	main()



