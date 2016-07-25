#!/usr/bin/env python3

# ne marche pas bien avec les divisions 
# si une règle est "à cheval" alors ça coince... 
# à vérifier : suppression du dernier token...

import sys

import os
import re
import codecs
import gc

from xml.dom.minidom import parse, parseString

sys.path.append("Corpindex")

from Cqpl import Cqpl
from Token import Token

class Transduction(object):

		
	def __init__(self,nomFic=""):
		self.cqpl = []
		self.action = []
		self.nomFic = nomFic
		self.listeTransition = []
		self.tableTransition = {}
		self.etat = 1
		self.tableauRequete = []
		self.requete = ''
		self.opt = False
		self.analyseurCqp = Cqpl()
		self.ltt = []

	# appel principal
	def addRules(self,r):
		self.analyseurCqp.putRequete(r)
		arbre = self.analyseurCqp.creationArbre()
		#print arbre
		self.initAnalyse()
		self.analyse(arbre,0,1)
		self.afnd2afd()
		self.ltt.append([self.listeTransition,self.tableTransition,self.modif])
	
	def initAnalyse(self):
		self.listeTransition = []
		self.tableTransition = {}
		self.modif = {}
		self.etat = 1 # 0 etat de depart 1 etat d'arrive, on commence a 2
		

	# construction de l'automate
	# le resultat est un dictionnaire à double entree ou :
	# 	- tab[etatdep][etatfin] = trans
	#	- si trans vaut -1, c'est une epsilon-transition
	# a est une liste de la forme [num regle, sous arbre1, sous arbre 2]
	# voir classe Cqpl pour les valeurs de a[0]
	def analyse(self,a,deb,fin):
		# gestion regles
		if a[0] == 1:		# regle ensmot : ensmot WITHIN GROUPE
			self.analyse(a[1])
		elif a[0] == 3:		#regle ensmot : ensmot ensmot %prec ET
			self.etat = self.etat + 1
			nv = self.etat
			self.analyse(a[1],deb,nv)
			self.analyse(a[2],nv,fin)
		elif a[0] == 9:		# regle ensmot :  ensmot "|" ensmot
			self.analyse(a[1],deb,fin)
			self.analyse(a[2],deb,fin)
		elif a[0] == 12:	# regle ensmot : "(" ensmot ")"
			self.analyse(a[1],deb,fin)
		elif a[0] == 15:	# regle ensmot : "(" ensmot ")" "?"
			self.analyse(a[1],deb,fin)
			self.ajouteTransition(deb,-1,fin)
		elif a[0] == 18:	# regle ensmot : mot
			self.analyse(a[1],deb,fin)
		elif a[0] == 21:	# regle mot : "[" motmod "]"
			self.analyse(a[1],deb,fin)
		elif a[0] == 27:	# regle motmod : defmot 
			if not a[1] in self.listeTransition:
				self.listeTransition.append(a[1])
			self.ajouteTransition(deb,self.listeTransition.index(a[1]),fin)
		elif a[0] == 30:	# regle motmod :  defmot "/" modif 
			if not a[1] in self.listeTransition:
				self.listeTransition.append(a[1])
			self.ajouteTransition(deb,self.listeTransition.index(a[1]),fin)
			posTr = self.listeTransition.index(a[1])
			self.lectureModification(a[2],posTr)
		elif a[0] == 24:		# regle mot : "[" motmod "]" "?"
			self.analyse(a[1],deb,fin)
			self.ajouteTransition(deb,-1,fin)

	
	# ajout d'une modification
	# dans le tableau de modification une modif est de la forme :
	# {num : {etiq:val,etiq:val,...}}
	def lectureModification(self,a,tr):
		pile = [a]
		res = {}
		cpt = 0
		if a[0] != 52:
			while len(pile)>0:
				a = pile.pop(0)
				#print("a="+str(a)) ####
				if a[0] == 51:	# regle modif : attval ',' attval
					pile.append(a[2])
					pile.append(a[1])
				elif a[0] == 48:	# regle modif : attval
					pile.append(a[1])
				elif a[0] == 46:
					res['*'] = '*'
				else:
					if a[1] in res: # gestion d'appels multiples à une même clef
						memo = res[a[1]]
						cpt+=1
						res[a[1]+str(cpt)] = memo
					
					res[a[1]] = a[2]
		#print(res) ####
		if tr not in self.modif:
			self.modif[tr] = []
			self.modif[tr].append(res)		
		else:
			self.modif[tr].append(res)

	
	# lecture modification et memorisation dans une table d'identificateurs
	# lmod  est de la forme [token,modif]
	# BUG si deux fois la même étiquette -> problème [c~"A"][l="et"][c~"^A"]
	def checkModif(self,lmod,modif):
		tableIdent = {}
		tableTrans = {}
		for elt in lmod:
			tok = elt[0]
			#print("modif=",modif,"elt=",elt[0].getLowStruct())
			if elt[1] in modif:
				mod = modif[elt[1]]
				#print("tablTrans=",elt[1],tableTrans)
				if elt[1] in tableTrans:
					tableTrans[elt[1]] += 1
				else:
					tableTrans[elt[1]] = 0
				pos = tableTrans[elt[1]]
				#print("mod=",mod,pos) ############
				for et in mod[pos]:
					if mod[pos][et][0] == '$':
						et = et[0] # bidouille !!!!!!!!!!!!!!
						ident = mod[pos][et][1:]
						if et[0] == 'f':
							tableIdent[ident] = tok.getForme()
						else:
							tableIdent[ident] = tok.getFeat(et)
		tableTrans = None
		modif = None
		mod = None
		return tableIdent

	
	# application des modifications
	def appliqueModif(self,ltok,modif):
		res = []
		#print("apliq="+str(ltok))
		#print ("ltok="+str(ltok)) ###
		#print ("modif="+str(modif)) ###
		ti = self.checkModif(ltok,modif)
		#print("ti="+str(ti))####
		tableTrans = {}
		ctag = False
		#print("liste modif ="+str(self.modif)) ###
		for elt in ltok:
			#print("ltok elt="+str(elt))
			#print("modif="+str(modif))
			tok = elt[0]
			if elt[1] in modif:
				#print("etiq="+str(tok.copyFeat(0)))
				etiqs = tok.copyFeat(0)
				etiqs['f'] = tok.getForme()
				mod = modif[elt[1]]
				#print("mod="+str(mod)) ###
				if len(mod[0])!=0:
					if elt[1] in tableTrans:
						tableTrans[elt[1]] += 1
					else:
						tableTrans[elt[1]] = 0
					pos = tableTrans[elt[1]]
					#print("appl mod="+str(mod)) ###
					cptTrans = 0
					if '*' in mod[pos].keys():
						cptTrans = 1
					else:
						#print("mod[pos]="+str(mod[pos]))
						for et in mod[pos].keys():
							#print("appl mod="+str(mod[pos][et])) ###
							if et == 'otag':
								#print '---> otag'
								res.append([[mod[pos][et]]])
								cptTrans = cptTrans + 1
							elif et == 'ctag':
								#print '--->ctag'
								cptTrans = cptTrans + 1
								ctag = True
							elif mod[pos][et][0] != '$':
								cptTrans = cptTrans + 1
								val = mod[pos][et]
								#print("ti="+str(ti))
								for i in ti:
									#print("i="+str(i),"ti="+ti[i],"val="+val)
									val = re.sub('#'+i,ti[i],val)
								et = re.sub('[0-9]+','',et)
								# fonctions
								#print("val transduc="+str(val))###
								try:
									#print("fonction -------->")
									# attention si val fait parti de python -> plante !!!
									nval = eval(val)
								except:
									#raise
									nval = val
									#print("valeur -------->")
								#print("resultat = ",et,nval)
								etiqs[et] = nval
					forme = etiqs['f']
					del etiqs['f']
					if cptTrans !=0:
						res.append(Token([forme,[etiqs]]))
					if ctag:
						res.append(Token(['/']))
						ctag = False
			else:
				res.append(tok)
			#print("res="+str(res)) ###
		tableTrans = None
		etiqs = None
		modif = None
		mod = None
		#ti = None
		return res
	
	# arbre d'analyse
	# noeud : forme,[{},{}]
	# retourne True/False
	def anaTrans(self,noeud,arbre):
		#print("anatrans="+str(noeud))
		#if len(noeud) != 1:
		if noeud != None:
			if arbre[0] == 46:  # mot quelconque (*)
				return True
			elif arbre[0] == 33:	# regle defmot : attval
				return self.anaTrans(noeud,arbre[1])
			elif arbre[0] == 36:	# regle defmot : attval '&' attval %prec ET
				return self.anaTrans(noeud,arbre[1]) and self.anaTrans(noeud,arbre[2])
			elif arbre[0] == 39:	# regle defmot : attval '|' attval
				return self.anaTrans(noeud,arbre[1]) or self.anaTrans(noeud,arbre[2])
			elif arbre[0] == 42:	# regle attval : ATT '=' VALATT
				return self.verifEgal(noeud,arbre[1],arbre[2])
			elif arbre[0] == 45:	# regle attval : ATT '~' VALATT
				return self.verifEreg(noeud,arbre[1],arbre[2])
			elif arbre[0] == 40:	# regle attval : '!' defmot
				return not self.anaTrans(noeud,arbre[1])
		else: # balise
			return False
	
	# test si un noeud verifie l'égalite 
	def verifEgal(self,noeud,att,val):
		valRet = False
		res = noeud
		if not noeud.isDiv():
			if att=='f':
				if val==noeud.getForme():
					res = noeud.clone()
					valRet = True
			else:
				f = []
				for i in range(0,noeud.getNum()):
					if noeud.getFeat(att,i) == val:
						f.append(noeud.copyFeat(i))
						valRet = True
				if valRet:
					res = Token([noeud.getForme(),f])
		self.matchNoeud = res
		return valRet
					
	
	# test si un noeud verifie l'égalite 
	def verifEreg(self,noeud,att,val):
		valRet = False
		res = noeud
		if not noeud.isDiv():
			if att=='f':
				if re.search(val,noeud.getForme()):
					res = noeud.clone()
					valRet = True
			else:
				f = []
				for i in range(0,noeud.getNum()):
					if re.search(val,noeud.getFeat(att,i)):
						f.append(noeud.copyFeat(i))
						valRet = True
				if valRet:
					res = Token([noeud.getForme(),f])
		self.matchNoeud = res
		return valRet
		
	
	## fin analyseur
	
	# algo AFN -> AFD (Dragon)
	# flemme de faire minimisation ... à faire
	# creation d'un tableau de transition de la forme :
	# {etat1:[[etatarr1,trans1],[etatarr2,trans2],...],etat2:[...],...}
	# l'ensemble des transitions sont stockes dans un tableau
	def epsilonSucc(self,T):
		res = []
		while len(T)>0:
			q = T.pop(0)
			if not q in res:
				res.append(q)
			if q in self.tableTransition:
				for e in self.tableTransition[q]:
					if e[1] == -1: # epsilon-transition
						if not e in res:
							res.append(e[0])
						if not e in T:
							T.append(e[0])
		res.sort()
		return res
		
	def calcTransition(self,E,tr):
		res = []
		for e in E:
			if e in self.tableTransition:
				for q in self.tableTransition[e]:
					if q[1] == tr:
						res.append(q[0])
		res.sort()
		return res
		
	def inListe(self,ll,l):
		for elt in ll:
			if (str(elt)==str(l)):
				return True
		return False
		
	def afnd2afd(self):
		Qp = []
		marque = []
		D = []
		q0 = self.epsilonSucc([0])	
		Qp.append(q0)
		marque.append(q0)
		while len(marque)>0:
			S = marque.pop(0)
			for a in range(0,len(self.listeTransition)):
				T = self.epsilonSucc(self.calcTransition(S,a))
				if len(T)>0:
					if not self.inListe(Qp,T):
						Qp.append(T)
						marque.append(T)
					D.append([str(S),a,str(T)])
		self.tableTransition = {}
		listeEtats = {'[0]':0,'[1]':1}
		numEtat = 2
		for t in D:
			if not t[0] in listeEtats:
				listeEtats[t[0]] = numEtat
				numEtat = numEtat + 1
			if not t[2] in listeEtats:
				listeEtats[t[2]] = numEtat
				numEtat = numEtat + 1
			self.ajouteTransition(listeEtats[t[0]],t[1],listeEtats[t[2]])

		
	## fct utils
	def ajouteTransition(self,edeb,trans,efin):
		if edeb in self.tableTransition:
			self.tableTransition[edeb].append([efin,trans])
		else:
			self.tableTransition[edeb] = []
			self.tableTransition[edeb].append([efin,trans])
				
	# accesseur
	def putRequete(self,requete):
		self.analyseurCqp.putRequete(requete)
	
	def getTableTransition(self):
		return self.ltt
		
	# parcours d'un flux de token et application de l'automate
	# pas de retour arrière pour l'analyse
	def checkTabToken(self,tabTok):
		#tabTok = [x.getLowStruct() for x in tabTok] # trnaformation temporaire
		#print("tabtok="+str(tabTok)) ###
		res = tabTok # table de règles vide
		longueurTab = len(tabTok)
		#print("tabTok="+str(len(tabTok))) ####
		#print("element tabtok"+str(tabTok)) ###
		#print(self.getTableTransition())
		for t in self.getTableTransition(): # pour chaque regle de transformation
			lTrans = t[0]	# regle transformation
			tTrans = t[1]	# table transition
			modif = t[2]	# modification
			n = 0		# etat de depart
			ptemp = 0
			ptok = -1	# position du token courant
			ltemp = []	# ensemble des tokens recouvrant une  regle
			res = []	# resultat d'une transformation
			rtemp = [] 	# tableau token temporaire
			while ptok <  len(tabTok)-1: 	# parcours de l'ensemble des tokens
				#print("------ etat="+str(n)) ########
				ptok = ptok + 1 	# position token suivant
				tokv = tabTok[ptok]	# recuperation du token
				#print("--->tokv="+str(tokv.getLowStruct())) ###########
				#ptemp = ptemp + 1	# position temporaire
				if False: #len(tokv) == 1:	# si balise MIS à FALSE POUR TESTER
					#ptemp = ptemp - 1 	# décrémente position temporaire
					res.append(tokv) 	# on remet le token courant dans le flux resultat
				else:			# sinon 
					trouve = False 	# booleen 'True' si il existe une transition
					for nc in tTrans[n]: # pour un etat on test tous les etats accessibles
						suivant = nc[0]		# etat atteignable
						transition = nc[1] 	# via la transition
						#print("nc="+str(nc)) ####
						if self.anaTrans(tokv,lTrans[transition]):	# si match
						#if self.anaTrans(tokv.getLowStruct(),lTrans[transition]):	# si match
							if transition in modif:
								infos = self.matchNoeud
							else:
								infos = tokv
							ltemp.append([infos,transition])
							#ltemp.append([self.matchNoeud,transition])
							n = suivant
							trouve = True
							break		# des que match on sort de la boucle
					if trouve:	# si match on enregistre le token
						#print ("A") ######
						#print("etat="+str(n)) #####
						rtemp.append(tokv)
						#print("rtemp="+str(rtemp)) ########
						if n == 1: # match et transformation (fin automate)
							#print("modif="+str(modif)) ##########
							#print("ltemp="+str(ltemp)) ##########
							ltok = None
							ltok = self.appliqueModif(ltemp,modif)
							res = res + ltok
							ptemp = 0
							ltemp = []
							rtemp = []
							n = 0
					else:		# si non match alors
						ltemp = []
						#print("B "+str(n)+ " ptok="+str(ptok)+" rtemp="+str(len(rtemp))) #########
						if n == 0: # parcours normal (debut automate)
							res.append(tokv)
							#print "ajout="+str(tokv)
						else: # le coup precedent etait dans l'automate
							#print ("ajout="+str(rtemp[0])) ###
							res.append(rtemp[0])
							ptok = ptok - len(rtemp) 
							n = 0		# reinitialisation de l'automate
						rtemp = []
			#for toktok in res:###
				#print("toktok="+str(toktok))###
			#for toktok in rtemp:###
				#print("rtemp="+str(toktok))###
			if len(rtemp) != 0:
				res = res + rtemp
			#print("res="+str(res))###
			tabTok = res
		#print("ltemp="+str(ltemp)) #####
		#res = res + self.appliqueModif(ltemp,{})
		#print(res)
		#res = [Token(x) for x in res] # modification temporaire
		#print("fin anatrans="+str(res[0]))
		return res
		
		
if __name__ == '__main__':
	from Tokenize import Tokenizer
	c = Transduction()
	c.addRules('[l="donner"/emploi="s1"][*]{0,3}[f="confiture"][f="aux"][f="cochons"]')
	n=c.ltt[0][0]
	t=c.ltt[0][1]
	for elt in range(0,len(n)):
		if n[elt][1][-1] == 46:
			n[elt] = '*'
		else:
			n[elt] = n[elt][1][-1]
	print("""
	<html>
<head>
  <meta charset="utf-8"/>
  <title>Reseau</title>
  <link rel="stylesheet" type="text/css" href="reseau.css" />
  <script type="text/javascript" src="reseaudata.js">_</script>
  <script type="text/javascript" src="reseaucore.js">_</script>
  <script type="text/javascript" src="reseaufunc.js">_</script>
  <script type="text/javascript" src="reseauevt.js">_</script>
</head>
<body onload="init()">
	<div id='global'>
		<p id="message"></p>
		<ul id="funct">
		<li><input id="efface" type="submit" onclick="invisible('efface')" value="Invisible"/></li>
		<li><input id="trans" type="submit" onclick="liensVisibles('trans')"value="Transition visible"/></li>
		<li><input id="allvisible" type="submit" onclick="allVisible()" value="Tout visible"/></li>
		<li><input id="init" type="submit" onclick="init()" value="Initialisation"/></li>
		</ul>
		<div id='container'>
			<div id="container">
			<canvas id="canvas" width="1000" height="600">
				Ce navigateur ne supporte pas HTML5 ... changez en !!
			</canvas>
		</div>
	</div>	
<div>	
	""")
	print('<ul id="noeuds">')
	for elt in t:
		print('<li name="'+str(elt)+'" num="'+str(elt)+'" couleur="#AAAAAA"/>')
	print('<li name="1" num="1" couleur="#ffffff"/>')
	print('</ul>')
	print('<ul id="liens">')
	for tr in t:
		for elt in t[tr]:
			valtr = str(n[elt[1]])
			print('<li deb="'+str(tr)+'" fin="'+str(elt[0])+'" value="'+valtr+'" mesure="1"/>')
	print('</ul>')
	print("""
		</div>	
		</body>
		</html>
		""")
