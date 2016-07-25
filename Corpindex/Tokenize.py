#!/usr/bin/python3

##
# LDI 2008
# Fabrice Issac
# Classe Tokenize
##
# tokenization d'un texte
# le dictionnaire est de la fome :
#           forme<tab>lemme<tab>etiquette...

import sys
import os
import re
import codecs
import string

sys.path.append("Corpindex")

from ply import *
from Dico import *
from Token import Token
from CorpException import *

class Tokenizer(object):
	def __init__(self,dicoMs,typeMs,dicoMc=[]):
		self.dico = Dico()
		self.listeDicoMs = dicoMs
		self.typeMs = typeMs
		self.listeDicoMc = dicoMc
		self.lexer = None
		self.listeToken = []
		self.etiquettes = []
		self.lexer = lex.lex(object=self,reflags=re.UNICODE)
		self.dictr = dict((ord(x), y) for (x, y) in zip('ABCDEFGHIJKLMNOPQRSTUVWXYZÂÀÉÊÈËÎÏÔÛÙÇ','abcdefghijklmnopqrstuvwxyzàâéèêëîïôûùç'))
		self.pileRes = []
		self.dicoMs = {}
		self.dicoMc = {}
		self.pileBalise = []
		
	# List of token names.   This is always required
	tokens = (
		'ABREV',
		'MOT',
		'WOUV',
		'WFER',
		'ATT',
		'VAL1',
		'VAL2',
		'FORME',
		'DIVOUV',
		'BALOUV',
		'BALSTA',
		'DIVFER',
		'PONCT_FAIBLE',
		'PONCT_FORT',
		'GUILLEMET',
		'OUVR',
		'FERM',
		'TIRET',
		'NUM',
		'QUOT',
		'APOS',
		'SYM'
	)
	# définition du mot
	matchmot = {}
	langue = 'df' # par defaut
	#matchmot['df'] = r"[^-<> .!?,;:|({\[)}\]0-9_%'\"\n\t\r+/@»*°=&]+'?" 
	matchmot['df'] = r"[^-<> .!?,;:…|({\[)}\]_%'\"\n\t\r+/@«»*°=&`“ㆍ‘” ‘’ⓒ~ ]+'?" #' avec espace insécable
	

	
	def t_DIVOUV(self,t):
		r'<[^/][^>]* id=["\'][^>]*["\']>'
		reg = re.match('<[^/][^>]* id="([^"]+)"',t.value)
		info = reg.group(1) #.decode('utf8')
		self.pileBalise.append(True)
		t.value = [[info]]
		#print("DIVOUV="+str(t.value)) #####
		return t
		
	def t_BALSTA(self,t):
		r'<[^/][^>]*/>'
		#print "DIVOUV="+t.value
		#print("BALISE STA "+t.value)####
		t.value = [t.value,[{'l':'TAG','c':'TAG'}]]
		#print(t)###
		return t
		
	def t_BALOUV(self,t):
		r'<[^/][^>]*>'
		#print "DIVOUV="+t.value
		#print("ELIMINATION BALISE "+t.value)####
		self.pileBalise.append(False)
		#t.value = [info]
		#return t
		
	def t_DIVFER(self,t):
		r'</[^>]*>'
		ferme = self.pileBalise.pop(-1)
		#print("Fermeture="+t.value+" "+str(ferme)) ####
		if ferme:
			t.value = ['/']
			return t
		
	def t_PONCT_FORT(self,t):
		r'(\.\.)?[.!?:;]|¿|¡'
		#r'(\.\.)?[.!?;:]|…'
		t.value = [t.value,[{'l':t.value,'c':'Fs'}]]
		return t

	def t_PONCT_FAIBLE(self,t):
		r','
		t.value = [t.value,[{'l':t.value,'c':'Fw'}]]
		return t
		
	def t_OUVR(self,t):
		r'[({\[]|«'
		#r'[({\[]|«'
		t.value = [t.value,[{'l':t.value,'c':'Fo'}]]
		return t
		
	def t_FERM(self,t):
		r'[)}\]]|»'
		#r'[)}\]]'
		t.value = [t.value,[{'l':t.value,'c':'Fc'}]]
		return t
		
	def t_NUM(self,t):
		r'[-+]?\d+'
		t.value = [t.value,[{'l':'0','c':'NUM'}]]
		return t
				
	def t_TIRET(self,t):
		r'[-—_]'
		t.value = [t.value,[{'l':'-','c':'Ft'}]]
		return t
		
	def t_APOS(self,t):
		r"[`'’]"
		t.value = ["'",[{'l':"'",'c':'Fq'}]]
		return t
		
	#def t_QUOT(self,t):
	#	r"'"
	#	t.value = [t.value,[{'l':"'",'c':'Fq'}]]
	#	return t
		
	def t_GUILLEMET(self,t):
		r'"'
		t.value = ["''",[{'l':'"','c':'Fg'}]]
		return t
		
	def t_SYM(self,t):
		r"[%\+*]"
		t.value = [t.value,[{'l':t.value,'c':'Fy'}]]
		return t
		
	# reconnaissance des mots 
	def t_MOT(self,t):
		mot = t.value
		listeInfos = self.dicoMs.get(mot)
		if not mot.islower() and mot not in 'à': # à expliquer
			motmin = mot.translate(self.dictr)
			#motmin = string.translate(mot,self.tr)
			listeInfos = listeInfos + self.dicoMs.get(motmin)
		if len(listeInfos) == 0:
				listeInfos = [{'l':t.value,'c':"?"}]
		t.value = [t.value,listeInfos]
		#print t
		return t

	t_MOT.__doc__ = matchmot[langue]
	

		
	# A string containing ignored characters (spaces and tabs)
	t_ignore  = ' \t\n\r\f\v'
	
	def t_error(self,t):
		#sys.stderr.write("Illegal character '%s'\n" % t.value[0])
		#sys.stderr.write("Illegal character '%s'" % t.value[0])
		#sys.stderr.write(" dans '%s'\n" % t.value)
		t.lexer.skip(1)
		
	# entree de la chaine a analyser
	def init(self,texte):
		#self.lexer.input(texte.lower())
		self.lexer.input(texte)
		self.texte = texte
	
	# recuperation du token suivant
	def getNextToken(self):
		tok = self.lexer.token()
		#print("gnt1 "+str(tok))###
		if not tok:
			#raise Exception("oups : "+self.texte) 
			raise TokError("oups : "+self.texte) 
		#print("gnt2 "+str(tok))
		return tok
	
	# recuperation dans un tableau de tous les tokens
	# ATTENTION ne marche pas si les tokens ne sont pas dans la même chaîne (pileLoc est remis à [])
	# pas génial !!!
	def calcTokens(self):
		self.pileRes = []
		pileLoc = []
		#dic = self.dicoMc.getDicoMc() # initialisation dictionnaire des UPL
		dic = self.dicoMc.getDictCw() # initialisation dictionnaire des UPL
		while True:
			try:
				nt = self.getNextToken() # récupération du token suivant
				forme = nt.value[0]
				#print(nt)###
				if len(nt.value) != 1: # ???
					#print("===== pileLoc ===> "+str(pileLoc))
					infos = nt.value[1] # listes informations 
					linfos = []
					clef = forme # par defaut la clef est la forme
					for k in list(infos[0].keys()): # ??? aussi
						c = k+':'+infos[0][k]
						if c in dic:
							clef = c
					#print("--------->  clef="+str(clef))
					if (clef in dic): # si appartient à UPL
						#print("--->empile "+forme) #######
						pileLoc.append([forme,infos])
						#print(" +++ ===== pileLoc ===> "+str(pileLoc))
						#print("dic["+clef+"]="+str(dic[forme]))
						infmc = dic[clef][0]
						dic = dic[clef][1]
						#print("dic="+str(dic))
						if len(dic)==0: # fin de mot
							#print("fin UPL -> infmc="+str(infmc))
							self.pileRes.append([self.depileMots(pileLoc),infmc])
							pileLoc = []
							dic = self.dicoMc.getDictCw()
					else: # n'est pas un élément d'une UPL
						#print("NON UPL -------->")
						for elt in pileLoc:
							#print("depile ===> "+str(elt))
							self.pileRes.append(elt)
						pileLoc = []
						dic = self.dicoMc.getDictCw()
						#dic = {}
						self.pileRes.append([forme,infos])
				else:
					self.pileRes.append([forme])
			#except Exception as e:
			except TokError as e:
				#print(e)
				#raise
				break
		#try:
		#	print "FinpileRes="+str(self.pileRes[-1])+" nt="+str(nt)
		#except:
		#	print "pileRes="+str(self.pileRes)+" nt="+str(nt)
		#print("pileRes "+str(self.pileRes))
		return [Token(x) for x in self.pileRes]
		#return self.pileRes
	
	# depile une pile de mot pour former un mot compose
	def depileMots(self,pile):
		elt = pile.pop(0)
		forme = elt[0]
		for m in pile:
			forme = forme + " " + m[0]
		return forme
		
	# lecture du dictionnaire des mots simples
	def readMs(self):
		self.dicoMs = Dico()
		self.dicoMs.load(self.listeDicoMs,self.typeMs)
				
	# lecture du dictionnaire des mots composés
	def readMc(self):
		self.dicoMc = Dico()
		self.dicoMc.load(self.listeDicoMc,"dicomc")
					

if __name__ == '__main__':
	pass			

