#sniffeur réseau
from scapy.all import sniff, IP, TCP, ARP
from collections import defaultdict
import signal
import sys

# Détection des scans de ports (ex: SYN scan)
port_scans = defaultdict(set)

# Détection des requêtes ARP suspectes
arp_requests = defaultdict(int)


# Gestion des interruptions propres
def signal_handler(sig, frame):
    print("\nArrêt du sniffer...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def detect_port_scan(packet):
    if packet.haslayer(TCP) and packet[TCP].flags == 2:  # Flag SYN uniquement
        src_ip = packet[IP].src
        dst_port = packet[TCP].dport
        port_scans[src_ip].add(dst_port)

        if len(port_scans[src_ip]) > 10:  # Seuil de détection ajustable
            print(f"[ALERTE] Scan de ports détecté depuis {src_ip}!")


def detect_arp_spoofing(packet):
    if packet.haslayer(ARP) and packet[ARP].op == 1:  # Requête ARP
        src_mac = packet[ARP].hwsrc
        src_ip = packet[ARP].psrc
        arp_requests[src_ip] += 1

        if arp_requests[src_ip] > 5:  # Seuil ajustable
            print(f"[ALERTE] Activité ARP suspecte détectée depuis {src_ip} ({src_mac})!")


def packet_callback(packet):
    if packet.haslayer(IP):
        print(f"{packet[IP].src} -> {packet[IP].dst} | {packet.summary()}")
        detect_port_scan(packet)
    if packet.haslayer(ARP):
        detect_arp_spoofing(packet)


print("Sniffer en cours d'exécution... (Ctrl+C pour arrêter)")
sniff(prn=packet_callback, store=False)
