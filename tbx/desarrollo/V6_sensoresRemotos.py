import arcpy
import os

arcpy.env.overwriteOutput = True



gdb = arcpy.GetParameterAsText(0)
arcillas = arcpy.GetParameterAsText(1)
oxidos = arcpy.GetParameterAsText(2)

fc_arcillas = arcpy.Dissolve_management(arcillas, 'in_memory\\arcillas', "#", '#', 'MULTI_PART', 'DISSOLVE_LINES')
fc_oxidos = arcpy.Dissolve_management(oxidos, 'in_memory\\oxidos', "#", '#', 'MULTI_PART', 'DISSOLVE_LINES')



def modificarCampos(fc_arcillas=fc_arcillas, fc_oxidos=fc_oxidos):
	camposArcillas = [x.name for x in arcpy.ListFields(fc_arcillas)]
	camposOxidos = [x.name for x in arcpy.ListFields(fc_oxidos)]
	for x in camposArcillas:
		try:
			arcpy.DeleteField_management(fc_arcillas, x)
		except:
			pass
	for x in camposOxidos:
		try:
			arcpy.DeleteField_management(fc_oxidos, x)
		except:
			pass
	arcpy.AddField_management(fc_arcillas, "TIPO_ARC", "TEXT", '#', '#', "50", '#', 'NULLABLE', 'NON_REQUIRED', '#')
	arcpy.AddField_management(fc_oxidos, "TIPO_OXI", "TEXT", '#', '#', "50", '#', 'NULLABLE', 'NON_REQUIRED', '#')

	for x in [[fc_arcillas, "TIPO_ARC", "Arcillas"], [fc_oxidos, "TIPO_OXI", "Oxidos"]]:
		with arcpy.da.UpdateCursor(x[0], [x[1]]) as cursorUC:
			for m in cursorUC:
				m[0] = x[2]
				cursorUC.updateRow(m)
		del cursorUC



def unionCapas(gdb=gdb, fc_arcillas=fc_arcillas, fc_oxidos=fc_oxidos):
	union = arcpy.Union_analysis([fc_arcillas, fc_oxidos], 'in_memory\\union', 'ALL', '#', 'GAPS')
	arcpy.AddField_management(union, "TIPO", "TEXT", '#', '#', "50", '#', 'NULLABLE', 'NON_REQUIRED', '#')
	with arcpy.da.UpdateCursor(union, ["TIPO", "TIPO_ARC", "TIPO_OXI"]) as cursorUC:
		for x in cursorUC:
			if x[1] != "" and x[2] != "":
				x[0] = "{} - {}".format(x[1], x[2])
			elif x[1] != "" and x[2] == "":
				x[0] = x[1]
				x[2] = '-'
			elif x[1] == "" and x[2] != "":
				x[0] = x[2]
				x[1] = '-'
			cursorUC.updateRow(x)
	del cursorUC
	arcpy.DeleteField_management(union, ["FID_arcillas", "FID_oxidos"])
	arcpy.Append_management(union, os.path.join(gdb, 'FD1_INSUMOS', 'PM_V6_SensoresRemotos'), "NO_TEST")
	arcpy.SetParameterAsText(3, os.path.join(gdb, 'FD1_INSUMOS', 'PM_V6_SensoresRemotos'))



def main():
	modificarCampos()
	unionCapas()



if __name__ == "__main__":
	main()




