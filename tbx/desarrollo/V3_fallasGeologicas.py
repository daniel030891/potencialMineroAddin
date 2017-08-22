import arcpy
import os
import json

arcpy.env.overwriteOutput = True

jsonfile = open(r'\\srvfile01\bdgeocientifica$\Addins_Geoprocesos\PotencialMinero\scripts\config_tools.json', 'r')
configTmp = json.load(jsonfile)
config = configTmp["fallasGeologicas"]
jsonfile.close()
del jsonfile


class fallGeo:
	def __init__(self):
		self.ws = arcpy.GetParameterAsText(0)
		self.fc = arcpy.GetParameterAsText(1)
		self.codi = arcpy.GetParameterAsText(2)
		self.desc = arcpy.GetParameterAsText(3)
		self.domains = config["domains"]
		self.msg = config["msg"]
		self.error = config["error"]
		self.information = []


	def consistency_01_desc(self):
		errores = [[1, x[0], x[1].lower()] for x in arcpy.da.SearchCursor(self.fc, ["OID@", self.desc]) if x[1].lower() not in self.domains["category"]]
		if len(errores) != 0:
			self.information.extend(errores)
		else:
			pass


	def process(self):
		arcpy.AddMessage("\n {}: {}... ".format(self.msg["m2"], os.path.basename(self.ws)))
		try:
			desc = arcpy.Describe(self.ws)
			if desc.datatype == u'Workspace':
				if arcpy.Exists(os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V3_FallasGeologicas')):
					if len(self.information) > 0:
						arcpy.AddMessage("  Errores:")
						arcpy.AddMessage("   {}: {}...".format(self.msg["m1"], self.desc))
						for x in self.information:
							e = self.error["e{}".format(x[0])]
							arcpy.AddWarning("    {}: FID: {}, Valor: {}".format(e, x[1], x[2]))
					else:
						arcpy.AddMessage("  {}...".format(self.msg["m3"]))
						copia = arcpy.CopyFeatures_management(self.fc, "in_memory\\fallasGeologicas")
						with arcpy.da.UpdateCursor(copia, [self.desc]) as cursorUC:
							for row in cursorUC:
								row[0] = row[0].lower()
								cursorUC.updateRow(row)
						del cursorUC
						campos = {"CODI": self.codi, "DESCRIPCION": self.desc}
						arcpy.DeleteRows_management(os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V3_FallasGeologicas'))
						for k, v in campos.items():
							arcpy.AlterField_management(copia, v, k)
						arcpy.Append_management(copia, os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V3_FallasGeologicas'), "NO_TEST")
						arcpy.SetParameterAsText(4, os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V3_FallasGeologicas'))
						arcpy.AddMessage("\n {}... \n".format(self.msg["m4"]))
						arcpy.AddMessage("\n {} \n".format(self.msg["m5"]))
				else:
					raise RuntimeError("\n {}... \n".format(self.error["e2"]))
			else:
				raise RuntimeError("\n {}... \n".format(self.error["e3"]))
		except Exception as e:
			arcpy.AddWarning(e)



	def main(self):
		self.consistency_01_desc()
		self.process()


if __name__ == "__main__":
	obj = fallGeo()
	obj.main()