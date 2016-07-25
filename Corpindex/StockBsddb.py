#!/usr/bin/python3
# -*- coding: utf-8 -*-

##
# LDI 2011
# Fabrice Issac
# Classe StockBsddb
##

import re
import pickle
import sys
import random
import time

try:
	import bsddb3 as bsddb
except ImportError:
	try:
		import bsddb
	except ImportError:
		sys.stderr.write("pas de prise en charge du module bsddb\n")

class Stock(dict):
	def __init__(self):
		self.dico = {}

	def open(self,name,mode="r"):
		try:
			self.dico = bsddb.btopen(name+".bsd",mode)
		except:
			sys.stderr.write("impossible d'ouvrir : "+name+"\n")
			raise

	def close(self):
		self.dico.close()
		
	def keys(self):
		return list(self.dico.keys())

	def __setitem__(self,c,v):
		try:
			self.dico[c.encode()]=v
		except:
			self.dico[c] = v
		
	def __getitem__(self,c):
		try:
			ret = self.dico[c]
		except TypeError:
			ret = self.dico[c.encode()]
		return ret
		
	def sync(self):
		self.dico.sync()

if __name__ == '__main__':
		pass

