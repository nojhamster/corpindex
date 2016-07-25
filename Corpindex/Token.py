#!/usr/bin/python3

##
# 2014
# Fabrice Issac
# Classe Token
##
# gestion des affichages des concordances

import string
import re
import sys
import json

class Token(object):
	'Classe Token'
	def __init__(self,tok):
		'Constructeur de l\'objet'
		self.__tok = tok

	def getForme(self):
		'Retourne la forme'
		return self.__tok[0]

	# ne concerne que le premier par défaut
	def getFeat(self,att,num=0):
		if not self.isDiv():
			if att == "f":
				return self.getForme()
			else:
				num = min(num,len(self.__tok[1]) - 1)
				return self.__tok[1][num][att]
		else:
			return ""

	def getNum(self):
		return len(self.__tok[1]) 
		
	def getDiv(self):
		if self.isDiv():
			return self.__tok[0][0]

	def isDiv(self):
		return (len(self.__tok) == 1)

	def getLowStruct(self):
		'return the <i>low level</i> structure'
		return self.__tok

	def getLstFeat(self,num=0):
		'return the list of the features'
		try:
			lst = list(self.__tok[1][num].keys())
		except:
			print(self.__tok)
			print(self.__tok[1][0].__tok)
			raise
		return lst
		
	def getJson(self):
		return json.dumps(self.__tok)
		
	def clone(self):
		'return a copy of the token'
		return Token(self.getLowStruct())
		
	def copyFeat(self,n):
		res = {}
		for elt in self.getLstFeat(n):
			res[elt] = self.getFeat(elt,n)
		return res
		
if __name__ == '__main__':
	pass			



