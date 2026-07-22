#!/usr/bin/env python3
"""
DNS Query Sniffer
Watches DNS query traffic on a network interface and prints unique domains
that don't match an exclude list.

Requires root/administrator privileges to open raw sockets.
"""

import argparse
import sys
from signal import SIGINT, signal

import scapy.all as scapy
from termcolor import colored

DEFAULT_EXCLUDE_KEYWORDS = ["google", "cloud", "bing", "static"]


class DNSSniffer:
    def __init__(
        self, interface: str, exclude_keywords: list[str], verbose: bool = False
    ):
        self.interface = interface
        self.exclude_keywords = exclude_keywords
        self.verbose = verbose
        self.domains_seen: set[str] = set()

    def _is_excluded(self, domain: str) -> bool:
        return any(keyword in domain for keyword in self.exclude_keywords)

    def process_packet(self, packet) -> None:
        if not packet.haslayer(scapy.DNSQR):
            return

        try:
            domain = packet[scapy.DNSQR].qname.decode(errors="ignore").rstrip(".")
        except Exception as exc:
            if self.verbose:
                print(colored(f"[!] Failed to decode query name: {exc}", "red"))
            return

        if domain in self.domains_seen:
            return
        if self._is_excluded(domain):
            return

        self.domains_seen.add(domain)
        print(colored(f"[!] Domain: {domain}", "green"))

    def start(self) -> None:
        print(
            colored(
                f"[+] Sniffing DNS queries on interface '{self.interface}'", "yellow"
            )
        )
        try:
            scapy.sniff(
                iface=self.interface,
                filter="udp and port 53",
                prn=self.process_packet,
                store=False,
            )
        except PermissionError:
            print(
                colored(
                    "[!] Permission denied. Try running as root/administrator.", "red"
                )
            )
            sys.exit(1)
        except OSError as exc:
            print(
                colored(
                    f"[!] Failed to open interface '{self.interface}': {exc}", "red"
                )
            )
            sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sniff and display unique DNS queries on a given interface."
    )
    parser.add_argument(
        "-i",
        "--interface",
        required=True,
        help="Network interface to sniff on (e.g. eth0, ens33, wlan0)",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        default=",".join(DEFAULT_EXCLUDE_KEYWORDS),
        help=f"Comma-separated keywords to exclude from output (default: {','.join(DEFAULT_EXCLUDE_KEYWORDS)})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show extra diagnostic output (e.g. decode failures)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    exclude_keywords = [kw.strip() for kw in args.exclude.split(",") if kw.strip()]

    def handle_sigint(signum, frame):
        print(colored("\n[!] Ctrl+C pressed. Exiting immediately...", "red"))
        sys.exit(1)

    signal(SIGINT, handle_sigint)

    sniffer = DNSSniffer(
        interface=args.interface,
        exclude_keywords=exclude_keywords,
        verbose=args.verbose,
    )
    sniffer.start()


if __name__ == "__main__":
    main()
