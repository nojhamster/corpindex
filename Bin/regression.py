#!/usr/bin/python3

# tests

import sys
import io

base = 'Cmd'
buildindex = 'buildidx.py'
query = 'query.py'
idx2xml = 'idxexport.py'
ficrules = "Francais.rul"

def execute(commande,params):
	print(commande,params)
	stdoutorig = sys.stdout
	sys.stdout = mystdout = io.StringIO()
	sys.argv = [commande]+params.split(" ")
	fic = open(commande).read()
	comp = compile(fic,'<string>','exec')
	d = dict(locals(), **globals())
	exec(comp,d,d)
	sys.stdout = stdoutorig
	return mystdout.getvalue()

def affiche(dico):
	for elt in dico:
		print(elt,end=" ")
		if dico[elt] == True:
			print("ok")
		else:
			print("pb : "+str(dico[elt]))
			
print(sys.argv)

requetes = '\'[c~"^V"][l="comme"][c~"D"][c~"^N"]\' \'[l="homme"]\' \'[c="N---"]\''
dicres = {}
dicresrule = {}
dicresreq = {}
stdoutorig = sys.stdout
for typebase in ['dpy','dbm','bsd']:
	try:
		res = execute(base+"/"+buildindex,"-d Dictionaries/Tests/test-dico-ms.dico -i Corpus/test.txt -lf f l c -v -db "+typebase)
		valeur = len(execute(base+"/"+idx2xml,"-o xml -i Corpus/test.txt"))
	except Exception as exc:
		valeur = str(exc)
		sys.stdout = stdoutorig
		#if sys.argv[1] == "-k":
		raise
	print(valeur)
	dicres[typebase] = True if valeur == 113540 else valeur
	try:
		res = execute(base+"/"+buildindex,"-d Dictionaries/Tests/test-dico-ms.dico -i Corpus/test.txt -lf f l c r -v -r Rules/"+ficrules+" -db "+typebase)
		valeur = len(execute(base+"/"+idx2xml,"-o xml -i Corpus/test.txt"))
	except Exception as exc:
		sys.stdout = stdoutorig
		valeur = str(exc)
		#if sys.argv[1] == "-k":
		raise
	print(valeur)
	dicresrule[typebase] = True if valeur == 85417 else valeur
	try:
		q = execute(base+"/"+query,"-i Corpus/test.txt -r 4 -q "+requetes)
		print(q)
		valeur = len(q)
	except Exception as exc:
		sys.stdout = stdoutorig
		valeur = str(exc)
		#if sys.argv[1] == "-k":
		raise
	print("query = ",typebase," = ",valeur)
	dicresreq[typebase] = True if valeur == 583 else valeur

print("Index seul")
affiche(dicres)
print("index - règles")
affiche(dicresrule)
print("requête")
affiche(dicresreq)
