import arcpy
import pythonaddins
import webbrowser
import threading
import json


jsonfile = open(r'\\srvfile01/bdgeocientifica$/Addins_Geoprocesos\PotencialMinero\scripts\config_addin.json')
config = json.load(jsonfile)
jsonfile.close()
del jsonfile
tbxattr = config["tbx"]
errorattr = config["error"]


class extensionIniciarSesion(object):
    pass



class iniciarSesion(object):
    """Implementation for addinProject_addin.login (Button)"""
    def __init__(self):
        self.enabled = False
        self.checked = False
    def onClick(self):
        pass



class V1_unidadesGeologicas(object):
    """Implementation for addinProject_addin.unidadesGeologicas (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        try:
            pythonaddins.GPToolDialog(tbxattr["path"], tbxattr["tools"]["ug"])
        except:
            pythonaddins.MessageBox(errorattr["e1"]["desc"], errorattr["e1"]["title"], errorattr["e1"]["tipo"])



class V3_fallasGeologicas(object):
    """Implementation for addinProject_addin.fallasGeologicas (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        try:
            pythonaddins.GPToolDialog(tbxattr["path"], tbxattr["tools"]["fg"])
        except:
            pythonaddins.MessageBox(errorattr["e1"]["desc"], errorattr["e1"]["title"], errorattr["e1"]["tipo"])


class V4_depositosMinerales(object):
    """Implementation for addinProject_addin.depositosMinerales (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        try:
            pythonaddins.GPToolDialog(tbxattr["path"], tbxattr["tools"]["dm"])
        except:
            pythonaddins.MessageBox(errorattr["e1"]["desc"], errorattr["e1"]["title"], errorattr["e1"]["tipo"])


class V5_geoquimica(object):
    """Implementation for addinProject_addin.geoquimica (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        try:
            pythonaddins.GPToolDialog(tbxattr["path"], tbxattr["tools"]["gq"])
        except:
            pythonaddins.MessageBox(errorattr["e1"]["desc"], errorattr["e1"]["title"], errorattr["e1"]["tipo"])


class V6_SesoresRemotos(object):
    """Implementation for addinProject_addin.sesoresRemotos (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        try:
            pythonaddins.GPToolDialog(tbxattr["path"], tbxattr["tools"]["sr"])
        except:
            pythonaddins.MessageBox(errorattr["e1"]["desc"], errorattr["e1"]["title"], errorattr["e1"]["tipo"])



class crearDirectorioTrabajo(object):
    """Implementation for addinProject_addin.workspace (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(tbxattr["path"], tbxattr["tools"]["ed"])



class potencialMinero(object):
    """Implementation for addinProject_addin.potencialMinero (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        pythonaddins.GPToolDialog(tbxattr["path"], tbxattr["tools"]["pm"])



def OpenBrowserURL():
    url = config["urlmanual"]
    webbrowser.open(url,new=0)



class abrirUrl(object):
    """Implementation for addinProject_addin.url (Button)"""
    def __init__(self):
        self.enabled = True
        self.checked = False
    def onClick(self):
        t = threading.Thread(target=OpenBrowserURL)
        t.start()
        t.join()