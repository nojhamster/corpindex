#!/usr/bin/python3

##
# LDI 2008
# Fabrice Issac
# Classe Index
##


from struct import *
import string
import zlib
import sys
import re

import pickle
import os
import glob
import shutil

sys.path.append("Corpindex")

from Token import Token
from Tokenize import Tokenizer
from Concordance import Concordance
from Tokxml import Tokxml

class Index(object):
	'The index class processes the indexation of the tokens in a corpus'
	def __init__(self,fileName,nature="bsd",verbose = False,ficlog=sys.stderr):
		self.ficlog = ficlog
		#self.length = length
		self.verbose = verbose
		self.fileName = fileName # ancien nomFichier
		self.tagList = []	 # ancien listeEtiquette
		self.tags = []		 # ancien etiquettes
		self.tagIndex = {}	 # ancien indexEtiquette
		self.globalIndexDB = {} # table persistante
		self.globalIndex = {"f":{}}
		#self.globalIndex["f"] = {}
		#self.indexGroupe = {} 					variable relique
		#self.regexpMot = re.compile('<w ?[^>]*>[^<]*')		variable relique
		#self.regexpAttributs = re.compile('[^= ]*="[^"]*"')	variable relique
		self.maxMot = 0;
		self.debug = '';
		self.nomRes = re.sub('^.*[\/\\\]','',self.fileName)
		self.nomRes = re.sub('\..*$','',self.nomRes)
		self.dirName = self.fileName+"_idx"	#ancien nomRep
		self.indexBD = None
		self.tokenizer = None
		#self.indexGroupeK = [] 				variable relique
		#self.documentOffset = None 				variable relique
		#self.document = None 					variable relique
		self.pileDiv = []
		self.indexDiv = {}
		self.indexDivDebFin = {}
		self.indexElement = {}
		self.indexPosElement = None
		self.numElement = 0
		self.zone = {}
		self.divBD = None
		# chargement du bon module en fonction de la nature de la BdD persistante utilisée
		#sys.path.append("Corpindex")
		n = self.getNature()
		if n != "" and nature == "": # index déjà créé
			nature = n
		#print("nature="+nature) ####
		if nature == "bsd":
			self.stock = __import__("StockBsddb")
		elif nature == "kcf":
			self.stock = __import__("StockKc")
		elif nature == "dpy":
			self.stock = __import__("StockDictPy")
		elif nature == "dbm":
			self.stock = __import__("StockDbm")
		else:
			self.ficlog.write("DB nature not found\n")
			exit(1)
		self.nature = nature

	# retourne le nom de l'index
	def getName(self):
		return self.fileName

	# initialisation du tokenizer
	def initTokenizer(self,type,listeD,typeD='dico',listeMc=[],lang="df"):
		if type == "txt":
			Tokenizer.langue = lang
			self.tokenizer = Tokenizer(listeD,typeD,listeMc)
			self.tokenizer.readMs()
			self.tokenizer.readMc()
		else:
			self.tokenizer = Tokxml()

	# initialisation du dossier pour la sauvegarde (effacement et création)
	def initDB(self): 			#ancien initBase
		"""Creates the directory where the index database is stored.
If a directory named "fileName_idx" already exists, it is overwritten.
Otherwise, a "fileName_idx" directory is created."""
		if os.path.isdir(self.dirName):
			try:
				shutil.rmtree(self.dirName)
			except OSError:
				self.ficlog.write("error 1: cannot delete directory\n")
		try:
			os.mkdir(self.dirName)
		except OSError:
			self.ficlog.write("error 2: cannot create directory\n")
			exit(0)

	# creation des fichiers (index, document) en utilisant des tables de hachage persistantes
	# gérées par l'objet "Stock" le jeu d'étiquette est nécessaire sous forme d'un tableau
	def createBase(self,tags):
		self.tags = tags
		self.divBD = self.stock.Stock()
		self.divBD.open(self.dirName+'/'+self.nomRes+'_div','w')
		self.indexBD = self.stock.Stock()
		self.indexBD.open(self.dirName+'/'+self.nomRes+'_index','w')
		self.indexBD['___listetiquette___'] = pickle.dumps(tags)
		self.indexBD['___nombremots___'] = "0"
		self.globalIndexDB = {}
		if isinstance(tags,str): # beurk
			tags = tags.split(":")
		for e in tags:
			self.globalIndexDB[e] = self.stock.Stock()
			self.globalIndexDB[e].open(self.dirName+'/'+self.nomRes+'.'+e,'w')
		self.indexElement = {}
		self.numElement = 0

	# retourne le type de base utilise pour stocker l'index (bsd, kcf)
	def getNature(self):
		nat = glob.glob(self.dirName+'/'+self.nomRes+'_index.*')
		if len(nat) > 0:
			return nat[0][-3:]
		else:
			return ""

	# sauvegarde de l'indexation
	def updateDB(self):
		lstEtiq = {'f':1}
		#print(self.tagList) ######
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndex[e].keys())
			lstEtiq[e] = 1
		self.tagIndex["f"] = list(self.globalIndex["f"].keys())
		for e in lstEtiq:
			#print(self.globalIndex.keys()) ##################
			for v in self.tagIndex[e]:
				if e in self.globalIndexDB:
					#self.ficlog.write(str(e)+' '+str(v)+'                          '+chr(13))
					#self.ficlog.write(str(e)+' '+str(v)+'\n')
					#print (self.globalIndexDB[e].keys())
					try:
						tmpvar = self.globalIndexDB[e][v]
						if tmpvar != None:
							prec = pickle.loads(tmpvar)
						else:
							prec = []
					except (TypeError,KeyError):
						#raise
						prec = []
					nouv = self.globalIndex[e][v]+prec
					try:
						p = pickle.dumps(nouv,2)
					except:
						sys.stderr.write(len(nouv))
						raise
					self.globalIndexDB[e][v] = p
			del self.globalIndex[e]
			self.globalIndex[e] = {}
		for e in list(self.globalIndexDB.keys()):
			self.globalIndexDB[e].sync()


	# création de l'index
	def indexation(self,tabTok,cptMot):
		for tokv in tabTok:
			#print(tokv.getLowStruct())
			forme = tokv.getForme()
			if not tokv.isDiv():
				cptMot += 1
				self.addTokenDocument(tokv)
				self.debug = forme
				if forme not in self.globalIndex["f"]:
					self.globalIndex["f"][forme] = [cptMot]
				else:
					self.globalIndex["f"][forme].append(cptMot)
				info = {}
				info["f"] = forme
				numetiquette = 0
				for i in range(0,tokv.getNum()):
					for etiquette in tokv.getLstFeat(i):
						val = tokv.getFeat(etiquette,i)
						try:
							self.globalIndex[etiquette][val].append(cptMot)
						except KeyError:
							try:
								self.globalIndex[etiquette][val] = [cptMot]
							except KeyError:
								self.globalIndex[etiquette] = {}
								self.globalIndex[etiquette][val] = [cptMot]
								self.tagList.append(etiquette)
			else: # division
				forme = tokv.getDiv()
				#print(forme)
				if forme == "/": # fin division
					[div,debut] = self.pileDiv.pop(-1)
					if div in self.indexDiv:
						if debut in self.indexDiv[div]:
							self.indexDiv[div][debut].append(cptMot+1)
						else:
							self.indexDiv[div][debut] = [cptMot+1]
					else:
						self.indexDiv[div] = {}
						self.indexDiv[div][debut] = [cptMot+1]
				else: # debut division
					self.pileDiv.append([forme,cptMot+1])
		return cptMot

	# indexation
	def indexTexte(self,trans=None):
		ptrfic = open(self.fileName,encoding='utf-8')
		cptMot = 0
		nbLigne = 0
		self.tagList = []
		offsetTotal = 0
		self.globalIndex = {}
		self.globalIndex["f"] = {}
		for ligne in ptrfic:
			nbLigne = nbLigne + 1
			if self.verbose:
				self.ficlog.write(str(nbLigne)+'    '+str(cptMot)+'                   '+chr(13))
			if ligne == "":
				break;
			# call tokeniser
			self.tokenizer.init(ligne)
			res = self.tokenizer.calcTokens()
			#print("token res = "+str(res)) ######
			# if transduction rules
			if trans:
				res = trans.checkTabToken(res)
			cptMot = self.indexation(res,cptMot)
			if cptMot % 1000000 == 0:
				#print("mise à jour") #####
				self.updateDB()
		self.updateDB()
		#print "-->"+str(self.globalIndexDB["f"].keys())
		cptMot = self.indexation([Token(['SENT',[{'l':'SENT','c':'SENT'}]])],cptMot)
		self.maxMot = cptMot
		# modif ici
		for e in self.tagList:
			if e in self.globalIndexDB:
				self.tagIndex[e] = list(self.globalIndexDB[e].keys())
		self.tagIndex["f"] = list(self.globalIndexDB["f"].keys())
		self.sauveBase()


	# lecture du fichier non etiquete
	def indexTexteBrut(self,trans=None):
		ptrfic = open(self.fileName,encoding='utf-8')
		cptMot = 0
		nbLigne = 0
		self.tagList = []
		offsetTotal = 0
		self.globalIndex = {}
		self.globalIndex["f"] = {}
		for ligne in ptrfic:
			nbLigne = nbLigne + 1
			if self.verbose:
				self.ficlog.write(str(nbLigne)+'    '+str(cptMot)+'                   ') #+chr(13))
			if ligne == "":
				break;
			#print(ligne)####
			# appel tokeniser
			self.tokenizer.init(ligne)
			res = self.tokenizer.calcTokens()
			#print("token res = "+str(res)) ######
			# si règle de transduction
			if trans:
				res = trans.checkTabToken(res)
			cptMot = self.indexation(res,cptMot)
			if cptMot % 1000000 == 0:
				#print("mise à jour") #####
				self.updateDB()
		self.updateDB()
		#print "-->"+str(self.globalIndexDB["f"].keys())
		cptMot = self.indexation([Token(['SENT',[{'l':'SENT','c':'SENT'}]])],cptMot)
		self.maxMot = cptMot
		# modif ici
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndexDB[e].keys())
		self.tagIndex["f"] = list(self.globalIndexDB["f"].keys())
		self.sauveBase()

	# transforme le texte XML en index
	def indexTexteXml(self):
		ptrfic = open(self.fileName,encoding='utf-8')
		self.tagList = []
		nbLigne = 0
		offsetTotal = 0
		while 1:
			try:
				ligne = ptrfic.readline()
				ligne = io.StringIO(ligne)
			except Exception(msg):
				self.ficlog.write("erreur lecture fichier ici :"+ligne+"\n")
				sys.exit(0)
			nbLigne = nbLigne + 1
			if nbLigne % 500000 == 0:
				print("mise à jour") #####
				self.updateDB()
			if self.verbose:
				self.ficlog.write(str(nbLigne)+'                  '+chr(13))
			if ligne == "":
				break;
			#self.tokenizer.init()
			for element in self.tokenizer.parse(ligne):
				tok = []
				infos = {}
				for av in element:
					if av[0] == 'f':
						tok.append(av[1])
					else:
						infos[av[0]] = av[1]
				tok.append([infos])
				self.addTokenDocument(tok)
				for attval in element:
					self.ajouteIndex(attval[0],attval[1],attval[2])
		self.maxMot = attval[2]
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndex[e].keys())
		self.tagIndex["f"] = list(self.globalIndex["f"].keys())


	# creation d'un index d'un tableau de token
	# par rapport à un index déjà créé et une table de modifications (transduction)
	def indexTokenTrans(self,idx,trans):
		cptMot = 0
		tagList = idx.getTagLists()
		for tabTokv in idx.getTokens():
			#for toktok in tabTokv:
				#print("avant="+str(toktok))###
			res = trans.checkTabToken(tabTokv)
			#print(res) ###
			cptMot = self.indexation(res,cptMot)
			res = None
			if self.verbose:
				self.ficlog.write(str(cptMot)+'                       '+chr(13))
		cptMot = self.indexation([Token(['SENT',[{'l':'SENT','c':'SENT'}]])],cptMot)
		self.maxMot = cptMot
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndex[e].keys())
		self.tagIndex["f"] = list(self.globalIndex["f"].keys())

	# creation d'un index d'un tableau de token
	# par rapport à un index déjà créé
	def indexToken(self,idx):
		cptMot = 0
		tagList = idx.getTagLists()
		for tabTokv in idx.getTokens():
			cptMot = self.indexation(tabTokv,cptMot)
			res = None
			if self.verbose:
				self.ficlog.write(str(cptMot)+'                       '+chr(13))
		cptMot = self.indexation([Token(['SENT',[{'l':'SENT','c':'SENT'}]])],cptMot)
		self.maxMot = cptMot
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndex[e].keys())
		self.tagIndex["f"] = list(self.globalIndex["f"].keys())

	# creation d'un index d'un tableau de token
	# par rapport à un index déjà créé et un dictionnaire
	def indexTokenDico(self,idx,dico):
		cptMot = 0
		tagList = idx.getTagLists()
		for tabTokv in idx.getTokens():
			res = []
			for tok in tabTokv:
				#print(tok)###
				if len(tok) != 1:
					tokres = dico.get(tok[0])
					if len(tokres) == 0:
						tokres = tok[1]
					else:
						print([tok[0],tokres])###
					res.append([tok[0],tokres])
				else:
					res.append(tok)
			cptMot = self.indexation(res,cptMot)
			if self.verbose:
				self.ficlog.write(str(cptMot)+'                       '+chr(13))
			res = None
		cptMot = self.indexation([Token(['SENT',[{'l':'SENT','c':'SENT'}]])],cptMot)
		self.maxMot = cptMot
		for e in self.tagList:
			self.tagIndex[e] = list(self.globalIndex[e].keys())
		self.tagIndex["f"] = list(self.globalIndex["f"].keys())

	# sauvegarde de l'indexation
	def sauveBase(self):
		# sauvegarde des divisions
		for d in self.indexDiv:
			self.divBD[d] = pickle.dumps(self.indexDiv[d])
		self.updateDB()
		self.indexBD['___listetiquette___'] = pickle.dumps(list(self.tagIndex.keys()))
		self.indexBD['___nombremots___'] = str(self.maxMot)
		for e in list(self.globalIndexDB.keys()):
			clef = open(self.dirName+'/'+self.nomRes+'.'+e+'_k','wb')
			pickle.dump(list(self.globalIndexDB[e].keys()),clef,2)
		self.indexPosElement = self.stock.Stock()
		self.indexPosElement.open(self.dirName+'/'+self.nomRes+'_element','w')
		for elt in self.indexElement:
			val = str(self.indexElement[elt])
			self.indexPosElement[val] = elt

	# lecture base
	def lectureBase(self):
		#print(self.dirName+'/'+self.nomRes+'_index')####
		self.indexBD = self.stock.Stock()
		self.indexBD.open(self.dirName+'/'+self.nomRes+'_index')
		self.maxMot = int(self.indexBD['___nombremots___'])
		# lecture fichiers documents
		self.fdocument = open(self.dirName+'/'+self.nomRes+'_document','rb')
		self.indexPosElement = self.stock.Stock()
		self.indexPosElement.open(self.dirName+'/'+self.nomRes+'_element')
		for e in pickle.loads(self.indexBD['___listetiquette___']):
			#e = e.decode()
			self.globalIndexDB[e] = self.stock.Stock()
			self.globalIndexDB[e].open(self.dirName+'/'+self.nomRes+'.'+e)
			if self.verbose:
				self.ficlog.write("init "+e+"\n")
			clef = open(self.dirName+'/'+self.nomRes+'.'+e+'_k','rb')
			self.globalIndex[e] = pickle.loads(clef.read())
		self.indexDiv = self.stock.Stock()
		self.indexDiv.open(self.dirName+'/'+self.nomRes+'_div')
		#print(self.dirName+'/'+self.nomRes+'_div')
		for div in list(self.indexDiv.keys()):
			if isinstance(div,bytes):
				div = div.decode('utf8')
			tabDiv = pickle.loads(self.indexDiv[div])
			#print(div,tabDiv)
			for deb in tabDiv:
				if deb not in self.indexDivDebFin:
					self.indexDivDebFin[deb] = {}
				for fin in tabDiv[deb]:
					if fin not in self.indexDivDebFin[deb]:
						self.indexDivDebFin[deb][fin] = []
					self.indexDivDebFin[deb][fin].append(div)
		self.lstDivDebSort = list(self.indexDivDebFin.keys())
		self.lstDivDebSort.sort()
		#print(self.lstDivDebSort)

	def close(self):
		if (self.verbose):
			sys.stderr.write("fermeture\n")
		for e in pickle.loads(self.indexBD['___listetiquette___']):
			self.globalIndexDB[e].close()
		self.fdocument.close()
		self.indexPosElement.close()
		self.indexBD.close()
		self.indexDiv.close()

	# ajoute element dans la structure ??
	def ajouteIndex(self,etiquette,valeur,pos):
		if etiquette not in self.globalIndex:
			self.globalIndex[etiquette] = {}
			self.globalIndex[etiquette][valeur] = [pos]
			self.tagList.append(etiquette)
		else:
			if valeur not in self.globalIndex[etiquette]:
				self.globalIndex[etiquette][valeur] = [pos]
			else:
				self.globalIndex[etiquette][valeur].append(pos)

	# retourne la liste des valeurs possible de chaque etiquette (forme comprise)
	def getTagIndex(self,e):
		return self.globalIndex[e]
		#return self.globalIndexDB[e].keys()

	# retourne la liste des offsets par rapport a une etiquette et sa valeur
	def getGlobalIndex(self,e,elt):
		try: # bof
			return pickle.loads(self.globalIndexDB[e][elt])
		except Exception as exc:
			#print(exc)
			return []



	# retourne les divisions à la position pos
	# sous forme d'un triplet [div,deb,fin]
	def getDivPos(self,pos):
		res = [""]
		maxi = len(self.lstDivDebSort) - 1
		fin = maxi
		if fin > 0:
			if not pos in self.lstDivDebSort:
				deb = 0
				m = deb
				termine = False
				while not termine:
					m = (deb + fin) // 2
					if pos > self.lstDivDebSort[m]:
						deb = m
					else:
						fin = m
					if fin - deb <= 1:
						termine = True
				if pos >= self.lstDivDebSort[deb] and pos <= self.lstDivDebSort[min(deb+1,maxi)]:
					respos = self.lstDivDebSort[deb]
				elif pos >= self.lstDivDebSort[fin] and pos <= self.lstDivDebSort[min(fin+1,maxi)]:
					respos = self.lstDivDebSort[fin]
				else:
					respos = self.lstDivDebSort[m]
			else:
				respos = pos
			for elt in self.indexDivDebFin[respos]:
				res.append([self.indexDivDebFin[respos][elt][0],respos,elt])
			if len(res)>1:
				res.pop(0)
		return res

	# retourne les position de la division 'div'
	# sous forme d'un tableau de couples debut,fin
	# NE SEMBLE PAS MARCHER
	def getPosDiv(self,div):
		res = []
		if div in self.indexDiv:
			tabDiv = pickle.loads(self.indexDiv[div])
			#print("-->",tabDiv)
			for debut in tabDiv:
				for fin in tabDiv[debut]:
					res.append([debut,fin])
		return res

	# retourne les position de la division 'div'
	# sous forme d'un tableau de couples debut,fin
	def getPosDivRegExp(self,rediv):
		res = []
		lstDiv = []
		#idxDivKeys = self.indexDiv.keys()
		for i in list(self.indexDiv.keys()):
			#print(type(rediv),rediv,i)###
			if re.search(rediv,i.decode('utf-8')):
				try:
					tabDiv = pickle.loads(self.indexDiv[i])
					for debut in tabDiv:
						for fin in tabDiv[debut]:
							res.append([debut,fin])
				except:
					pass
		return res

	# retourn le nom du dossier contenant les indexes
	def getIndexDirectory(self):
		return self.dirName

	# retourne la liste possible des étiquettes
	def getTagLists(self):
		return pickle.loads(self.indexBD['___listetiquette___'])

	# enlever un élément dans l'index à un offset donné
	def removeglobalIndex(self,e,elt,offset):
		tabtmp = self.getGlobalIndex(e,elt)
		try:
			tabtmp.remove(offset)
		except:
			pass
		self.globalIndexDB[e][elt] = pickle.dumps(tabtmp)

	# def intialisation fichiers documents
	def initFicDocument(self):
		for fic in glob.glob(self.dirName+'/'+self.nomRes+'.*'):
			os.remove(fic)
		self.fdocument = open(self.dirName+'/'+self.nomRes+'_document_tmp','wb')

	# création fichier document version 3 (current)
	def addTokenDocument(self,tok):
		lltok = tok.getLowStruct()
		#print(lltok)
		val = zlib.compress(pickle.dumps(lltok))
		if val in self.indexElement:
			self.fdocument.write(pack("i",int(self.indexElement[val])))
		else:
			self.numElement += 1
			self.indexElement[val] = str(self.numElement)
			self.fdocument.write(pack("i",self.numElement))

	# changement nom fichiers documents
	def renameFicDocument(self):
		#print(self.fdocument.name)####
		self.fdocument.close()
		chemin = self.dirName+'/'+self.nomRes
		if os.path.isfile(chemin+'_document'):
			os.remove(chemin+'_document')
		os.rename(chemin+'_document_tmp',chemin+'_document')

	def closeBase(self):
		self.indexBD.close()
		for e in list(self.globalIndexDB.keys()):
			self.globalIndexDB[e].close()
		self.indexPosElement.close()
		#print(self.divBD)####
		if self.divBD != None:
			self.divBD.close()
		self.fdocument.close()
		#self.documentOffset.close()

	# creation fichier de méta informations
	def createMeta(self):
		meta = open(self.dirName+'/'+self.nomRes+"_meta.xml","w",encoding='utf-8')
		meta.write("<meta>\n")
		meta.write("\t<list>\n")
		meta.write("\t\t<item k='tag' v='f:"+":".join(self.tagList)+"'>")
		meta.write("\t</list>\n")
		meta.write("</meta>\n")
		meta.close()

	# retourne une information (forme ou etiquette) par rapport a son offset et le type de l'etiquette
	def getElement(self,offset):
		format = calcsize("i")
		self.fdocument.seek((int(offset)-1)*format)
		elt = self.fdocument.read(format)
		#print("elt="+str(elt)+" offset="+str(offset))###
		pos = unpack("i",elt)[0]
		res = pickle.loads(zlib.decompress(self.indexPosElement[str(pos)]))
		try:
			res.append(self.zone[offset])
		except KeyError:
			pass
		return res

	# retourne la requete dans un contexte
	# debut : debut
	# fin : fin
	# taille : nb mots contextes
	def getResultat(self,debut,fin,taille,zone=[]):
		res = []
		pg = []
		pd = []
		#print("zone="+str(zone)) #####
		for i in range(max(1,debut-taille),max(1,debut)):
			pg.append(self.getElement(i))
		for i in range(debut,fin+1):
			#print(debut,fin,i)#####
			elt = self.getElement(i)
			#if i in zone:
			#	#print ("=-=-=->"+str(elt)) ###
			#	elt.append(zone[i])
			res.append(elt)
		for i in range(fin+1,min(fin+taille+1,self.maxMot)):
			pd.append(self.getElement(i))
		#print(res) ####
		try:
			divPos = self.getDivPos(debut)
		except IndexError:
			divPos = []
		return [pg,res,pd,divPos]

	# retourne la requete dans un contexte dans un tableau associatif
	# debut : debut
	# fin : fin
	# taille : nb mots contextes
	def getResultConc(self,debut,fin,taille,zone=[]):
		pv = []
		pl = []
		pr = []
		for i in range(max(1,debut-taille),max(1,debut)):
			pl.append(Token(self.getElement(i)))
		for i in range(debut,fin+1):
			pv.append(Token(self.getElement(i)))
		for i in range(fin+1,min(fin+taille+1,self.maxMot)):
			pr.append(Token(self.getElement(i)))
		try:
			divPos = self.getDivPos(debut)
		except IndexError:
			divPos = [""]
		return Concordance(pl,pv,pr,divPos,debut)

	# retourne le nombre de mots du document
	def getMaxMot(self):
		return self.maxMot

	# retourne
	def getTabResultats(self,tabres,taille,nb,zone=[]):
		"""
	tabres : tableau de résultats
	taille : taille du contexte
	nb : nombre de concordance
		"""
		res = []
		resort = list(tabres.keys())
		resort.sort()
		if nb !=-1:
			resort = resort[:nb]
		for rk in resort:
			#print(rk)####
			if rk<self.maxMot:
				yield self.getResultat(tabres[rk],rk,taille,zone)
#			res.append(self.getResultat(tabres[rk],rk,taille))
#		return res

	# retourne
	def getTabConc(self,tabres,taille,nb):
		"""
	retourne un tableau de concordances
	tabres : tableau de résultats
	taille : taille du contexte
	nb : nombre de concordance
		"""
		res = []
		resort = list(tabres.keys())
		resort.sort()
		if nb !=-1:
			resort = resort[:nb]
		for rk in resort:
			#print(rk)####
			if rk<self.maxMot:
				yield self.getResultConc(tabres[rk],rk,taille)

	# retourne l'ensemble du document via un iterateur
	# par paquet de 10000 (par defaut)
	def getTokens(self,fenetre=1000):
		pileFin = [-1] # sentinelle
		le = self.getTagLists()
		le.remove('f')
		cpt = 0
		ret = []
		for offset in range(1,self.getMaxMot()):
			#print "offset="+str(offset)
			cpt = cpt + 1
			if offset in self.indexDivDebFin: # si balise ouvrant ici
				#print offset
				for fin in sorted(self.indexDivDebFin[offset].keys()):
					for div in self.indexDivDebFin[offset][fin]:
						ret.append(Token([self.indexDivDebFin[offset][fin]]))
					pileFin.append(fin)
			tok = self.getElement(offset)
			ret.append(Token(tok))
			while offset in pileFin:
				ret.append(Token(['/']))
				pileFin.remove(offset)
			if cpt == fenetre:
				yield ret
				ret = []
				cpt = 0
		yield ret

	# retourne l'ensemble du document via un iterateur
	# par paquet de 10000 (par defaut)
	def getIndexTokens(self):
		offset = 1
		pileFin = [-1] # sentinelle
		while offset < self.getMaxMot():
			if offset in self.indexDivDebFin: # si balise ouvrant ici
				for fin in sorted(self.indexDivDebFin[offset].keys(), reverse=True):
					for div in self.indexDivDebFin[offset][fin]:
						yield Token([self.indexDivDebFin[offset][fin]]) # balise ouvrante
					pileFin.append(fin)
			tok = self.getElement(offset)
			offset += 1
			yield Token(tok) # token
			while offset == pileFin[-1]:
				del pileFin[-1]
				yield Token([['/']])	# balise fermante

	# associer des zones à un index (old)
	def putZone(self,zone):
		self.zone = zone

if __name__ == '__main__':
	pass
