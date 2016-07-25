#!/usr/bin/python3

import sys
import io

# création de l'instance
def createInstance(conf):
	return Texte(conf)

# greffon
class Texte(object):
	def __init__(self,param):
		valret = param["value"]
		self.closeFic = False
		if isinstance(valret,str):
			if param["value"] != "":
				self.ficout = open(param["value"] ,"w",encoding="UTF-8")
				self.closeFic = True
			else:
				self.ficout = sys.stdout
		elif isinstance(valret,io.StringIO):
			self.ficout = valret
		else:
			self.ficout = sys.stdout
		self.attaff = param["att"]
		self.res = []
		
	def traite(self,conc,pre=""):
		pl = conc.getLeftString(self.attaff)
		pv = conc.getPivotString(self.attaff)
		pr = conc.getRightString(self.attaff)
		infodiv = conc.getDiv()
		res = "_top"
		if len(infodiv) > 0:
			if infodiv[0] != '':
				res = infodiv[0][0]
		res += "\t"+"\t".join([str(conc.getOffset()),pl,pv,pr]) 
		#res += "\t"+str(conc.getOffset())
		self.ficout.write(pre+"\t"+res+"\n")
				
	def close(self):
		if self.closeFic:
			self.ficout.close()
		
