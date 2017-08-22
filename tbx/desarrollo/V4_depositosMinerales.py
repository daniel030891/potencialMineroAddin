import arcpy
import os
import json

arcpy.env.overwriteOutput = True

jsonfile = open(r'\\srvfile01\bdgeocientifica$\Addins_Geoprocesos\PotencialMinero\scripts\config_tools.json', 'r')
configTmp = json.load(jsonfile)
config = configTmp["depositosMinerales"]
jsonfile.close()
del jsonfile


class depoMin:
	def __init__(self):
		self.ws = arcpy.GetParameterAsText(0)
		self.fc = arcpy.GetParameterAsText(1)
		self.grade = arcpy.GetParameterAsText(2)
		self.value = arcpy.GetParameterAsText(3)
		self.domains = config["domains"]
		self.msg = config["msg"]
		self.error = config["error"]
		self.information = []


	def consistency_01_Grado(self):
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


	def process(self):
		arcpy.AddMessage("\n {}: {}... ".format(self.msg["m3"], os.path.basename(self.ws)))
		try:
			desc = arcpy.Describe(self.ws)
			if desc.datatype == u'Workspace':
				if arcpy.Exists(os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V4_DepositosMinerales')):
					if len(self.information) > 0:
						arcpy.AddMessage("  Errores:")
						for x in self.information:
							e = self.error["e{}".format(x[0])]
							arcpy.AddWarning("   {}: FID: {}, Valor: {}".format(e, x[1], x[2]))
					else:
						arcpy.AddMessage("  {}...".format(self.msg["m4"]))
						copia = arcpy.CopyFeatures_management(self.fc, "in_memory\\depositosMinerales")
						with arcpy.da.UpdateCursor(copia, [self.grade]) as cursorUC:
							for row in cursorUC:
								row[0] = row[0].lower()
								cursorUC.updateRow(row)
						del cursorUC
						campos = {"GRADO": self.grade, "VALOR": self.value}
						arcpy.DeleteRows_management(os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V4_DepositosMinerales'))
						for k, v in campos.items():
							arcpy.AlterField_management(copia, v, k)
						arcpy.Append_management(copia, os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V4_DepositosMinerales'), "NO_TEST")
						arcpy.SetParameterAsText(4, os.path.join(self.ws, 'FD1_INSUMOS', 'PM_V4_DepositosMinerales'))
						arcpy.AddMessage("\n {}... \n".format(self.msg["m5"]))
						arcpy.AddMessage(" {} \n".format(self.msg["m6"]))
				else:
					raise RuntimeError("\n {}... \n".format(self.error["e3"]))
			else:
				raise RuntimeError("\n {}... \n".format(self.error["e4"]))
		except Exception as e:
			arcpy.AddWarning(e)



	def main(self):
		self.consistency_01_Grado()
		self.consistency_02_Value()
		self.process()


if __name__ == "__main__":
	obj = depoMin()
	obj.main()