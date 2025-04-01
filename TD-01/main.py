##scanner de ports
import threading
from socket import socket


#Definir une fonction qui va scanner un port specifique
def scan_port(host, port):
    try:
        #creation d'un objet socket
        sock = socket(socket.AF_INET, socket.SOCK_STREAM)
        #definir un delai pour eviter le timout et blocage
        sock.settimeout(1)
        #tentative de connexion sur le port (0 si la connexion a reussi)
        result = sock.connect_ex((host, port))
        #si le port est ouvert (result == 0), on l'affiche
        if result == 0:
            print(f"[+] Port {port} est ouvert")
        #on ferme le socket
        sock.close()
    except Exception as e:
            #gestion des erreurs
            print(f"[-] Erreur sur le port {port}: {e}")
    #on demande a l'utilisateur l'adresse ip de la cible
target = input("entrez l'ip à scanner : ")

#on demande la plage d'adresse a scanner
start_port = int(input("Port de debut"))
end_port = int(input("Port de fin"))
#on informe l'utilisateur qu'on commence le scan
print(f"\n[***] scan target {target} sur les ports {start_port} a {end_port} [***]\n")
for port in range (start_port, end_port+1):
    #on cree un thread (execution parallele) pour chaque port
    t = threading.Thread(target=scan_port, args=(target, port))
    t.start()