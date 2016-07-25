#!/usr/bin/python3

##
# LDI 2008
# Fabrice Issac
# Classe Dico
##

import pickle
import re
import sys

#sys.path.append('../Proteus')
#sys.path.append('/home/fabrice/Developpe/Proteus')

try:
	from Analyse import *
except:
	pass
# lecture et gestion des dictionnaires
class Dico(object):
	'The Dico class loads and manages the dictionnaries'
	def __init__(self):
		self.type = ''
		self.dictSw = {} #Simple word dictionary (former dicoMs)
		self.dictCw = {} #Compound word dictionary (former dicoMc)
	

	def load(self,fileList,type='dico'):
		""" initialises the dictionaries:
		defines the dictionary type and the files to use
		possible file types : dico,proteus
		chooses the loading function according to the class type
		"""
		self.type = type
		if (type == 'dico'):
			for fileDict in fileList:
				self.loadDict(fileDict)
		elif (type == 'sdico'):
			for fileDict in fileList:
				self.loadSDict(fileDict)
		elif (type == 'proteus'):
			self.loadProteus(fileList[0],fileList[1])
		elif (type == 'dicomc'):
			for fileDict in fileList:
				self.loadDictCw(fileDict)
		
		
	
	
	def loadDict(self,nameFileDict):
		"""reads the simple word dictionaries (with .dico extension) from a file of the following format
		form<tab>lemma<tab>tag<tab>...
		the first line of the file must start with '>' and contain tag names separated by tabulation
		"""
		#position of the inflected form
		inflPos = 0
		dictCheck = {}
		#creates a new dictionary with the same keys as simple word Dictionary to check 
		#whether an inflected form has already been loaded
		dictCheck.fromkeys(list(self.dictSw.keys()))	
		try:
			filePtr = open(nameFileDict,encoding='utf-8')	
			#cpt =0
			for line in filePtr.readlines():			
				#cpt = cpt + 1
				#print str(cpt)
				#+'                       '+chr(13),
				if line.startswith('>'):
					#treatment of the first line of the dictionary file
					tags = line[1:].rstrip().split("\t")
					inflPos = tags.index('f')
					tags.remove('f')					
				elif not line.startswith('#'):
					infos = line.rstrip().split("\t")
					#infos = [x.encode() for x in line.rstrip().split("\t")]					
					inflForm = infos.pop(inflPos)				
					if inflForm in dictCheck:
					#adds a new dictionary to the list of dictionaries					
						#loads a serialised list of dictionaries for the given inflected form
						tmpDict = pickle.loads(self.dictSw[inflForm])
						#creates a dictionary with tags as keys and info as values
						newDict = dict(list(zip(tags,infos)))
						#adds a new dictionary to the list of dictionaries
						tmpDict.append(newDict)
					else:
						#adds a new dictionary list for the inflected form
						tmpDict = [dict(list(zip(tags,infos)))]
					dictCheck[inflForm] = 1
					self.dictSw[inflForm] = pickle.dumps(tmpDict) 
		except Exception as e:
			sys.stderr.write(e)
			sys.stderr.write('error: reading of a simple words dictionary file')
			raise
			exit
			
	
	def loadDictCw(self,nameFileDict):
		'reads the compound word dictionary'
		try:
			filePtr = open(nameFileDict,encoding='utf-8')
			for line in filePtr.readlines():
				if line.startswith('>'):
					tags = line[1:].rstrip().split("\t")
					inflPos = tags.index('f')
					tags.remove('f')
				elif not line.startswith('#'):
					infos = line.rstrip().split("\t")
					lwords = infos.pop(inflPos).replace("-"," - ").replace("'","' ").split(" ")
					dico = self.dictCw
					for m in lwords:
						if not m in dico:
							nd = {}
							dico[m] = [{},nd]
							prec = dico
							dico = nd
						else:
							dico = dico[m][1]
					if m in prec:
						prec[m][0] = [dict(list(zip(tags,infos)))]
					else:
						prec[m] = [[dict(list(zip(tags,infos)))],{}]
					# pas d'ambiguité pour les composés
		except:
			sys.stderr.write('error: reading of a compound word dictionary file ['+line.rstrip()+']['+nameFileDict+']\n')
			raise
			exit
			

	
	
	def loadSDict(self,nameDictSer):
		'reads dictionary from a serialised file'
		newDictSer = open(nameDictSer,'r')
		self.dictSw = pickle.load(newDictSer)
		
	
	def loadProteus(self,dossierTables,filePtrLemmes):
		'reads proteus dictionary'
		self.ana = Analyse(dossierTables,filePtrLemmes)
			
	
	def writeSDict(self,nameDictSer):
		'writes the serialised dictionary representation into a file'
		newDictSer = open(nameDictSer,'w')
		pickle.dump(self.dictSw,newDictSer)
		newDictSer.close()
		
	
	def get(self,inflForm):
		'dictionary access'
		try:
			if (self.type == 'dico' or self.type == 'sdico'):
				return self.getDict(inflForm)
			elif (self.type == 'proteus'):
				return self.getProteus(inflForm)
		except:
			return []
		
	
	def getDictCw(self):
		'compound word dictionary access'
		return self.dictCw
		
	
	def getDict(self,inflForm):
		'access to a dictionary in the hash table form'
		return pickle.loads(self.dictSw[inflForm])
		
	
	def getProteus(self,inflForm):
		'proteus dictionary access'
		return self.ana.analyse(inflForm)


if __name__ == '__main__':
	pass
	
