import arcpy
import os
import json


arcpy.env.overwriteOutput = True


jsonfile = open(r'\\srvfile01\bdgeocientifica$\Addins_Geoprocesos\PotencialMinero\scripts\config_tools.json', 'r')
configTmp = json.load(jsonfile)
config = configTmp["unidadesGeologicas"]
jsonfile.close()
del jsonfile


class unidGeo:
	def __init__(self):
		self.ws = arcpy.GetParameterAsText(0)
		self.fc = arcpy.GetParameterAsText(1)
		self.codi = arcpy.GetParameterAsText(2)
		self.grade = arcpy.GetParameterAsText(3)
		self.value = arcpy.GetParameterAsText(4)
		self.condition = arcpy.GetParameterAsText(5)
		self.params = arcpy.GetParameterInfo()
		self.domains= config["domains"]
		self.msg = config["msg"]
		self.error = config["error"]
		self.information = []



	def consistency_01_Grade(self):
		arcpy.AddMessage("\n {}: {}...".format(self.msg["m1"], self.grade))
		errores = [[1, x[0], x[1].lower()] for x in arcpy.da.SearchCursor(self.fc, ["OID@", self.grade]) if x[1].lower() not in self.domains["grade"]]
		if len(errores) != 0:
			self.information.extend(errores)
		else:
			pass


	def consistency_02_Value(self):
		arcpy.AddMessage(" {}: {}...".format(self.msg["m2"], self.value))
		errores = [[2, x[0], x[1]] for x in arcpy.da.SearchCursor(self.fc, ["OID@", self.value]) if x[1] < self.domains["value"]["min"] and x[1] > self.domains["value"]["max"]]
		if len(errores) != 0:
			self.information.extend(errores)
		else:
			pass


	def consistency_03_Condition(self):
		arcpy.AddMessage(" {}: {}...".format(self.msg["m3"], self.condition))
		errores = [[3, x[0], x[1].lower()] for x in arcpy.da.SearchCursor(self.fc, ["OID@", self.condition]) if x[1].lower() not in self.domains["condition"]]
		if len(errores) != 0:
			self.information.extend(errores)
		else:
			pass


	def consistency_04_Nulls(self):
		arcpy.AddMessage(" {}...".format(self.msg["m4"]))
		for x in self.params[2:6]:
			for m in arcpy.da.SearchCursor(self.fc, ["OID@", x.valueAsText]):
				if m[0] == None:
					self.information.append([4, x.valueAsText])
				else:
					pass



	def process(self):
		arcpy.AddMessage("\n {}: {}... ".format(self.msg["m5"], os.path.basename(self.ws)))
		try:
			desc = arcpy.Describe(self.ws)
			if desc.datatype == u'Workspace':
				if arcpy.Exists(os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V1_UnidadesGeologicas')):
					if len(self.information) > 0:
						arcpy.AddMessage("  Errores:")
						for x in self.information:
							e = self.error["e{}".format(x[0])]
							arcpy.AddWarning("   {}: FID: {}, Valor: {}".format(e, x[1], x[2]))
					else:
						arcpy.AddMessage("  {}...".format(self.msg["m5"]))
						copia = arcpy.CopyFeatures_management(self.fc, "in_memory\\unidadesGeologicas")
						with arcpy.da.UpdateCursor(copia, [self.grade, self.condition]) as cursorUC:
							for row in cursorUC:
								row[0], row[1] = row[0].lower(), row[1].lower()
								cursorUC.updateRow(row)
						del cursorUC
						campos = {"CODI": self.codi, "GRADO": self.grade, "VALOR": self.value, "CONDICION": self.condition}
						arcpy.DeleteRows_management(os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V1_UnidadesGeologicas'))
						for k, v in campos.items():
							arcpy.AlterField_management(copia, v, k)
						arcpy.Append_management(copia, os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V1_UnidadesGeologicas'), "NO_TEST")
						arcpy.SetParameterAsText(6, os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V1_UnidadesGeologicas'))
						arcpy.AddMessage("\n {}... \n".format(self.msg["m6"]))
						arcpy.AddMessage(" {} \n".format(self.msg["m7"]))
				else:
					raise RuntimeError("\n {}... \n".format(self.error["e5"]))
			else:
				raise RuntimeError("\n {}... \n".format(self.error["e6"]))
		except Exception as e:
			arcpy.AddWarning(e)




	def main(self):
		self.consistency_01_Grade()
		self.consistency_02_Value()
		self.consistency_03_Condition()
		self.consistency_04_Nulls()
		self.process()



if __name__ == "__main__":
	obj = unidGeo()
	obj.main()