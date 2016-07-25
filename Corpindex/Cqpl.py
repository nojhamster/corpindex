#!/usr/bin/env python3

# -----------------------------------------------------------------------------
# analyse de la requete avec ply
# -----------------------------------------------------------------------------
# TODO
#	- negation (en fait je ne sais pas trop)
# 	- fonctions (cf. CQP)
# liste regles :
#	 1 -> ensmot : ensmot WITHIN GROUPE
#	 2 -> ensmot : ensmot WITHIN NUM
#	 3 -> ensmot : ensmot ensmot %prec ET
#	 9 -> ensmot :  ensmot "|" ensmot
#	12 -> ensmot : "(" ensmot ")"
#	15 -> ensmot : "(" ensmot ")" "?"
#	18 -> ensmot : mot
#	21 -> mot : "[" motmod "]"
#	24 -> mot : "[" motmod "]" "?"
#	27 -> motmod : defmot
#	30 ->	| defmot "/" modif
#	31 ->	| defmot ZONE NUM
#	33 -> defmot : attval
#	34 ->	| "(" defmot ")"
#	36 ->	| defmot '&' defmot %prec ET
#	39 ->	| defmot '|' defmot
#	40 ->	| '!' defmot
#	42 -> attval : ATT '=' VALATT 
#	45 ->	| ATT '~' VALATT 
#	46 ->	| MOT
#	48 -> modif : attval
#	51 -> 	| attval ',' attval
#	52 ->	|

import sys
import os
import re

sys.path.append("Corpindex")

from ply import *


class Cqpl(object):
	tokens = ()
	precedence = ()

		
	def __init__(self):
		self.arbre = []
		# a garder pour debug
		self.debug = 0
		try:
			modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
		except:
			modname = "parser"+"_"+self.__class__.__name__
		self.debugfile = modname + ".dbg"
		self.tabmodule = modname + "_" + "parsetab"
	
		# Build the lexer and parser
		self.lex = lex.lex(module=self, debug=self.debug)
		self.yacc = yacc.yacc(module=self,
			debug=self.debug,
			debugfile=self.debugfile,
			tabmodule=self.tabmodule)

	# appel principal
	def creationArbre(self):
		self.arbre = []
		try:
			self.yacc.restart()
		except:
			pass
		try:
			self.yacc.parse(self.requete,lexer = self.lex)
		except Exception as msg:
			sys.stderr.write(str(msg)+"\n")
		return self.arbre

	# etats
	states = (
		('groupe','exclusive'),
		('zone','exclusive')
		)
		
	# tokens
	tokens = (
		'ATT','VALATT','WITHIN','GROUPE','MOT','NUM','ZONE'
		)
	
	literals = ['=', '~','[',']','{', '}', ',','(',')', '&', '|','?', '$', '/','!']

	# Tokens

	t_VALATT= r'"[^"]+"'
	t_ATT	= r'[a-z0-9]+'
	t_MOT	= r'\*'

	t_ignore = " \t\n"
	t_groupe_ignore = " \t\n"
	t_zone_ignore = " \t\n"
	
	def t_WITHIN(self,t):
		r'within'
		t.lexer.begin('groupe')
		return t
		
	def t_ZONE(self,t):
		r'\#'
		t.lexer.begin('zone')
		return t
    	
	def t_groupe_GROUPE(self,t):
		r'(~"[^"]+")|([A-z0-9][-_.A-z0-9]+)'
		t.lexer.begin('INITIAL')
		return t
		
	def t_groupe_NUM(self,t):
		r'[0-9]+'
		t.lexer.begin('INITIAL')
		return t
    	
	def t_zone_NUM(self,t):
		r'[0-9]+'
		t.lexer.begin('INITIAL')
		return t
    	
	def t_error(self, t):
		#sys.stderr.write("Illegal character '%s'" % t.value[0])
		t.lexer.skip(1)
		
	def t_groupe_error(self, t):
		#sys.stderr.write("Illegal character '%s'" % t.value[0])
		t.lexer.skip(1)

	def t_zone_error(self, t):
		#sys.stderr.write("Illegal character '%s'" % t.value[0])
		t.lexer.skip(1)

	#
	# Parsing rules
	#
	precedence = (
		('left','ET'),
		('left','|'),
	)
		
	def p_expr_groupe(self,p):
		'ensmot : ensmot WITHIN GROUPE'
		p[0] = [1,p[1],p[3]]
		self.arbre = p[0]

	def p_expr_groupe_num(self,p):
		'ensmot : ensmot WITHIN NUM'
		p[0] = [2,p[1],p[3]]
		self.arbre = p[0]

	def p_expr(self, p):
		'ensmot :  ensmot ensmot %prec ET'
		p[0] = [3,p[1],p[2]]
		self.arbre = p[0]
		
	def p_expr_ou(self, p):
		'ensmot :  ensmot "|" ensmot'
		p[0] = [9,p[1],p[3]]
		self.arbre = p[0]
				
	def p_expr_parenthese(self, p):
		'ensmot : "(" ensmot ")"'
		p[0] = [12,p[2]]
		self.arbre = p[0]
		
	def p_expr_parenthese_opt(self, p):
		'ensmot : "(" ensmot ")" "?"'
		p[0] = [15,p[2]]
		self.arbre = p[0]

	def p_expr_mot(self, p):
		'ensmot : mot'
		p[0] = [18,p[1]]
		self.arbre = p[0]
		
		 
	def p_mot(self,p):
		"""
		mot : '[' motmod ']'
			| '[' motmod ']' '?'
		"""
		if len(p)==4:
			p[0] = [21,p[2]]
		else:
			p[0] = [24,p[2]]			
			
	def p_motmod(self,p):
		"""
		motmod : defmot
			| defmot "/" modif
			| defmot ZONE NUM
		"""
		if len(p) == 2: # defmot
			p[0] = [27,p[1]]
		elif p[2] == "/": # modif
			p[0] = [30,p[1],p[3]]
		else: # zone
			p[0] = [31,p[1],p[3]]

				
	def p_defmot(self,p):
		"""
		defmot : attval
			| defmot '&' defmot  %prec ET
			| defmot '|' defmot
			| '(' defmot ')'
			| '!' defmot
		"""
		if len(p)>2:
			if p[2] == '|':
				p[0] = [39,p[1],p[3]]
			elif p[2] == '&':
				p[0] = [36,p[1],p[3]]
			elif p[1] == '!':
				p[0] = [40,p[2]]
			else:
				p[0] = [34,p[2]]
		else:
			p[0] = [33,p[1]]


	def p_attval(self,p):
		"""
		attval : ATT '=' VALATT 
			| ATT '~' VALATT
			| MOT
		"""
		if len(p)>2:
			if p[2] == '=':
				p[0] = [42,p[1],p[3][1:-1]]
			else:
				p[0] = [45,p[1],p[3][1:-1]]
		else:
			p[0] = [46]

	def p_modif(self,p):
		"""
		modif : attval
			| modif ',' attval
			|
		"""
		if len(p)==2:
			p[0] = [48,p[1]]
		elif len(p) == 4:
			p[0] = [51,p[1],p[3]]
		else:
			p[0] = [52]
 
 
	def p_error(self, p):
		#sys.stderr.write("erreur de syntaxe at '%s'" % p.value)
		tok = yacc.token()
		#sys.stderr.write(str(tok))
		raise Exception("Erreur de syntaxe vers _"+p.value+"_ dans _"+self.requete+"_")
	
	## fin analyseur
		
	# accesseur
	def putRequete(self,requete):
		self.requete = self.preProcQuery(requete)

	# affichage
	def affiche(self,niv,a):
		print(niv*'\t'+'['+str(a[0]))
		for i in range(1,3):
			try:
				if isinstance(a[i],list):
					self.affiche(niv+1,a[i])
				else:
					print(niv*'\t'+a[i])
			except:
				pass
		print(niv*'\t'+']')

	# preprocess pour gérer les {x,y} et {x}
	def preProcQuery(self,q):
		res = q
		for elt in re.finditer('(?P<tok>\[(\*|\(?[a-z]+[=~]"[^"]+"\)?( *(\||&) *)?)+(#[0-9]+)?\]){((?P<start>[0-9]+)(?P<sep>,))?(?P<end>[0-9]+)}',q):
			t = elt.group(0)
			start = elt.group("start")
			end = elt.group("end")
			sep = elt.group("sep")
			tok = elt.group("tok")
			if sep == None:
				trep = tok*int(end)
			else:
				trep = tok*int(start) + (tok+"?")*int(end)
			res=res.replace(t,trep)
		return res
	
if __name__ == '__main__':
	c = Cqpl()
	#exp = '[a="jkkkj"/a="c"][*]'
	#exp = '[f~"^(Francilien|Européen|Français|Allemand|Canadien)s?$"#1][*][c~"^V"#2]'
	#exp = '[a="a"]([b="b"/a="c"]?[c="c"/a="b"]|[d="d"]?)?[e="e"]'
	exp = '[a="aaa"][b="bbb"][c="ccc"]'
	c.putRequete(exp)
	msg=""
	res = c.creationArbre()
	if len(res) > 0:
		print(res)
		print(c.affiche(0,res))
 	 
 
