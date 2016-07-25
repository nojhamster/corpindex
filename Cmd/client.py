#!/usr/bin/python3

import socket
import sys
import argparse
import json

# lecture paramètres
parser = argparse.ArgumentParser(description="interrogation d'un index")
parser.add_argument("-v", "--verbose", help="active affichage informations",action="store_true",default=False)
parser.add_argument('-H', "--host", type=str, help='serveur distant',default='localhost')
parser.add_argument('-p', "--port", type=int, help='port du serveur distant',default=12357)
parser.add_argument("-q", "--query", type=str, help="requête CQPL",default="")

args = parser.parse_args()
args = vars(args)

host = args["host"] 
port = args["port"]
data = args["query"]

if data == "":
	out = False
	print("Client Corpindex")

reste = True
while reste:
	if out:
		reste = False
	else:
		data = sys.stdin.readline()
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((host, port))
		sock.sendall(bytes(data + "\n", "utf-8"))
		received = ''
		while True:
			tmp = str(sock.recv(1024), "utf-8")
			if len(tmp) == 0:
				break
			received += tmp
	except:
		print("erreur !")
		sock.close()
	sock.close()
	if received != "":
		r = json.loads(received)
		if not isinstance(r,str):
			for elt in r:
				print("\t".join(elt))
		else:
			print(r)
