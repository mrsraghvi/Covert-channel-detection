# sender/sender_tcp.py
"""
Real TCP-based timing sender. Sends small TCP SYN packets spaced to encode bits.
Requires administrative privileges and scapy. USE IN LAB ONLY.
"""
import time
import argparse
from scapy.all import IP, TCP, send

DELAY_SHORT = 0.02
DELAY_LONG = 0.12

def send_covert_tcp(dest_ip: str, dest_port: int, bitstring: str, repeat: int = 1):
    for r in range(repeat):
        for b in bitstring:
            pkt = IP(dst=dest_ip)/TCP(dport=dest_port, flags="S")
            send(pkt, verbose=False)
            time.sleep(DELAY_SHORT if b == "0" else DELAY_LONG)
        time.sleep(0.1)
    print(f"[+] Sent {len(bitstring)*repeat} TCP SYN packets to {dest_ip}:{dest_port}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dest", help="destination IP")
    parser.add_argument("port", type=int, help="destination port")
    parser.add_argument("bits", help="bitstring to send")
    parser.add_argument("--repeat", type=int, default=1)
    args = parser.parse_args()
    print("WARNING: sending packets on a real network. Make sure you have permission.")
    send_covert_tcp(args.dest, args.port, args.bits, args.repeat)
