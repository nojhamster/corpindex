#!/usr/bin/python3

import argparse
import sys
import glob
import os.path
import os
import socketserver
import re
import random
import io
import json

# lecture paramètres
parser = argparse.ArgumentParser(description="interrogation d'un index")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument('-i', "--index", nargs='+', type=str, help='fichier index',required=True)
parser.add_argument('-p', "--port", type=int, help='port du serveur distant',default=12357)
parser.add_argument('-d', "--dic", type=str, help='dictionnaire',default="")
args = parser.parse_args()
args = vars(args)

verb = args['verbose']
lstindex = args['index']
port = args["port"]
dic = args["dic"]

base = os.path.dirname(os.path.abspath(__file__))+"/.."

sys.path.append(base+"/Corpindex")
sys.path.append(base+"/Corpindex/greffon")

from RequeteIndex import RequeteIndex as Requete
from Post import Post
from Index import Index
from Dico import Dico


if dic != "":
	dictionnaire = Dico()
	dictionnaire.load([dic])
else:
	dictionnaire = None
tidx = []
for index in lstindex:
	if verb:
		print(index)
	idx = Index(index,"",verb)
	idx.lectureBase()
	tidx.append(idx)

recom = re.compile('([A-Z]+[a-z]*) (.*)')
reconf = re.compile('([a-z]+) ([0-9]+)')

conf = {"range":3,"taille":100}
# Classe Serveur
class Server(socketserver.BaseRequestHandler):
	
	def handle_timeout(self):
		print("timeout")
	
	def handle(self):
		global tidx
		global conf
		res = ""
		try:
			data = self.request.recv(1024).strip().decode('utf8').rstrip()
			print(data)
			comarg = recom.search(data)
			if comarg:
				com = comarg.group(1)
				arg = comarg.group(2)
				print("com=",com,"arg=",arg)
				if com == "CQPL":
					res = json.dumps(self.query(arg))
				elif com == "DIC":
					if dictionnaire:
						res = json.dumps(dictionnaire.get(arg))
				elif com[:5] == "PLAIN":
					argplain = self.genPlain(arg,com[5:])
					res = json.dumps(self.query(argplain))
				elif com == 'CONT':
					res = json.dumps(self.getContext(arg))
				elif com == "SET":
					param = reconf.search(arg)
					if param:
						 conf[param.group(1)] = int(param.group(2))
					res = json.dumps(["ok"])
				else:
					res = json.dumps(["commande inconnue"])
					print('commande inconnue')
		except:
			raise
			pass
		print("{} wrote".format(self.client_address[0]))
		self.request.send(bytes(res,'utf-8'))

		
	def query(self,data):
		global conf
		verb = True
		req = Requete()
		restotal = []
		tabinfo = []
		tabconc = []
		nbrestotal = 0
		r = conf["range"]
		taille = conf["taille"]
		print("Requête : "+data)
		for i in range(0,len(tidx)):
			idx = tidx[i]
			req.putIndex(idx)
			req.putRequete(data)
			res = req.calculRequete()
			nbrestotal += len(res)
			print('resultat : '+str(len(res)))
			restotal.append([idx,res,data,i])
		for elt in restotal:
			[idx,res,ident,nbi] = elt
			tabinfo.append([str(i)])
			info = len(tabinfo) - 1
			for pos in idx.getTabConc(res,r,taille):
				tabconc.append([info,pos])
		#nfic = "conc_"+str(random.random())+".txt"
		ptFic = io.StringIO("")
		print('Calcul concordances... ')
		params = {'att': 'f', 'type': 'out', 'id': '1', 'value': ptFic, 'name': 'ci_txt'}
		post = Post(params,tabconc,tabinfo)
		post.process()
		print("fait")
		return [nbrestotal,[x.split("\t") for x in ptFic.getvalue().split("\n")]]
			
	def genPlain(self,req,p):
		t = req.split(" ")
		if p[0] == 'f':
			tq = ['[f="'+x+'"]' for x in t]
		elif p[0] == 'l':
			tq = []
			for elt in t:
				tmp = {}
				tl = dictionnaire.get(elt)
				for tok in tl:
					tmp[tok["l"]] = 1
				tq.append('['+"|".join(['l="'+x+'"' for x in tmp])+']')
		if p[1] == 'e':
			res = '[*]{0,2}'.join(tq)
		elif p[1] == 'r':
			res = "".join(tq)
		return res
		
	def getContext(self,arg):
		[offset,t,nbi] = arg.split(" ")
		tc = 50 # taille du contexte
		idx = tidx[int(nbi)]
		do = int(offset)
		fo = do + int(t)
		d = max(1,do-tc)
		f = min(do+tc,idx.getMaxMot())
		res = " ".join([idx.getElement(p)[0] for p in range(d,do)])
		res += " <pivot>"
		res += " ".join([idx.getElement(p)[0] for p in range(do,fo)])
		res += "</pivot> "
		res += " ".join([idx.getElement(p)[0] for p in range(fo,f)])
		res = re.sub(" ([.,)])","\\1",res)
		res = re.sub("(['(]) ","\\1",res)
		res = re.sub(" - ","-",res)
		return(res)
	
##############


host = ""
server = socketserver.TCPServer((host, port), Server)
server.timeout = 4
print("Serveur Corpindex v0.1")
server.serve_forever()




