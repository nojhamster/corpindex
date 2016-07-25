#!/usr/bin/python3

##
# LDI 2014
# Fabrice Issac
##
import re
import sys
import os
import argparse
import json

# parameters
parser = argparse.ArgumentParser(description="interrogation d'un index")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument("-n", "--nosep", help="résultat sur une seule ligne",action="store_true",default=False)
parser.add_argument("-o", "--output", help="type de sortie",default="txt",choices=['txt','xml','json','dico','xml'])
parser.add_argument('-i', "--index", type=str, nargs='+',help='fichiers index',required=True)
parser.add_argument('-ident', "--identifiant", help='identifiant',default = "")
args = parser.parse_args()
args = vars(args)

index = args['index']
output = args['output']
ident = args['identifiant']
verb = args["verbose"]
nosep = args["nosep"]

tabul = '\t'
nl = '\n'
if nosep:
	tabul = ''
	nl = ''

# path to library
sys.path.append(os.path.dirname(sys.argv[0])+"/../Corpindex")

from Index import Index

if verb:
	sys.stderr.write(index)

for elt in index:
	idx = Index(elt,"")
	idx.lectureBase()
	op = ""
	div = ""
	if output == "xml":
		print("<text>",end=nl)
		if ident != "":
			print('<div id="'+ident+'">',end=nl)
	elif output == "json":
		print("[")
	for tok in idx.getIndexTokens():
		if output == "json":
			print(tok.getJson(),",",end=nl)
		elif output == "txt":
			op += tok.getFeat("f")+" "
			if tok.getFeat("f") in [".",";","?","!"]:
				op = re.sub(" ([,.])","\\1",op)
				op = re.sub("(') ","\\1",op)
				op = re.sub(" - ","-",op)
				print(op,end=nl)
				op = ""
		elif output == "xml":
			if tok.isDiv():
				div = tok.getDiv()
				if div == "/":
					print("</div>",end=nl)
				else:
					print('<div id=\"'+tok.getDiv()+'">',end=nl)
			else:
				print("<tok>"+nl+tabul+"<infos>",end=nl)
				for i in range(0,tok.getNum()):
					print(tabul*2+"<item ",end="")
					print(" ".join([att+'="'+tok.getFeat(att,i)+'"' if tok.getFeat(att,i)!='"' else att+"=\"''\"" for att in tok.getLstFeat(i)]),end="")
					print("/>",end=nl)
				print(tabul+"</infos>"+nl+tabul+"<w>"+tok.getForme()+"</w>",end=nl)
				print("</tok>",end=nl)
		elif output == "dico":
			if tok.isDiv():
				div = tok.getDiv()+"\t"
			else:
				print(div+"\t".join([tok.getFeat("f"),tok.getFeat("l"),tok.getFeat("c")]))
	if output == "xml":
		if ident != "":
			print("</div>",end=nl)
		print("</text>")
	elif output == "json":
		print('["FIN"]\n]')
