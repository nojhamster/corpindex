#!/usr/bin/python3

##
# 2014
# Fabrice Issac
# Classe Concordance
##
# gestion des concordances
# une concordance c'est : une partie gauche, un pivot, une partie droite et des divisions

import string
import re
import sys

from CorpException import *

class Concordance(object):
	'''
	Stockage d'une concordance 
	'''
	def __init__(self,pl,pv,pr,div,offset):
		self.__pl = pl
		self.__pv = pv
		self.__pr = pr
		self.__div = [x.decode('utf8') if isinstance(x,bytes) else x for x in div]
		self.__offset = offset
	
	def getLeft(self):
		return self.__pl

	def getLeftString(self,att="f"):
		return " ".join([x.getFeat(att) for x in self.__pl])

	def getRight(self):
		return self.__pr

	def getRightString(self,att="f"):
		return " ".join([x.getFeat(att) for x in self.__pr])

	def getPivot(self):
		return self.__pv

	def getPivotString(self,att="f"):
		return " ".join([x.getFeat(att) for x in self.__pv])

	def getDiv(self):
		return self.__div
		
	def getOffset(self):
		return self.__offset

