#!/usr/bin/python3

import argparse
import sys
import glob
import os.path
import os

# lecture paramètres
parser = argparse.ArgumentParser(description="informations sur un index")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument('-i', "--index", type=str, nargs='+',help='fichiers index',required=True)
args = parser.parse_args()
args = vars(args)

base = os.path.dirname(os.path.abspath(__file__))+"/.."

sys.path.append(base+"/Corpindex")
sys.path.append(base+"/Corpindex/greffon")

from RequeteIndex import RequeteIndex as Requete
from Post import Post
from Index import Index

verb = args['verbose']
index = args['index']

req = Requete()
restotal = []
nbrestotal = 0
try:
	for f in index:
		idx = Index(f,"",verb)
		idx.lectureBase()
		if verb:
			sys.stderr.write('fin initialisation base\n')
		print(f+"\t"+str(idx.getMaxMot()))
except Exception as err:
	if err.args[0] == 24:
		print("Too many open files, try the '-l' option")
	else:
		raise
		print("Error !")
