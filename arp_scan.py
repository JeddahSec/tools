#!/usr/bin/env python3

import argparse
import sys
from signal import SIGINT, signal

from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import srp
from termcolor import colored


def default_sigint_handler(signum, frame):
    print(colored("\n[!] Ctrl+C pressed. Exiting immediately...", "red"))
    sys.exit(1)


signal(SIGINT, default_sigint_handler)


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Fast network discovery tool using Address Resolution Protocol (ARP) requests."
    )
    parser.add_argument(
        "-t",
        "--target",
        required=True,
        help="Target IP address or network range (e.g., 192.168.1.1 or 192.168.1.0/24)",
    )
    return parser.parse_args().target


def scan(ip_address):
    print(colored(f"[*] Sending ARP broadcasts to target: {ip_address}", "cyan"))

    # Crafting the packet: ARP Request bundled inside an Ethernet Broadcast layer
    arp_request = ARP(pdst=ip_address)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_packet = broadcast / arp_request

    # Send and receive packets at Layer 2 (srp)
    try:
        answered, _ = srp(arp_request_packet, timeout=2, verbose=False)
    except PermissionError:
        print(
            colored(
                "\n[-] Error: Root privileges required to send raw Layer 2 packets.",
                "red",
            )
        )
        print(colored("    Please run this script using 'sudo'.", "yellow"))
        sys.exit(1)

    if not answered:
        print(colored("[-] No active hosts responded to the ARP request.", "yellow"))
        return

    # Print results in a structured format
    print(colored("\n[+] Discovered Hosts:", "magenta"))
    print("-" * 50)
    print(f"{'IP Address':<20}{'MAC Address':<30}")
    print("-" * 50)

    for sent, received in answered:
        # Extract IP and MAC fields directly from the response layer
        print(f"{received.psrc:<20}{received.hwsrc:<30}")

    print("-" * 50)


def main():
    target = get_arguments()
    scan(target)


if __name__ == "__main__":
    main()
