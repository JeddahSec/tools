#!/usr/bin/env python3
"""
HTTP Request & Plaintext Credential Sniffer

Watches HTTP requests on an interface, logs visited URLs, and flags
raw payloads that look like they might contain submitted login fields.

Note: this only sees *unencrypted* HTTP. Any HTTPS traffic (the vast
majority of real-world logins today) is invisible to this tool unless
you're also terminating TLS separately (e.g. via a proxy/downgrade),
which this script does not do.

For use only on networks/devices you own or are explicitly authorized
to test.
"""

import argparse
import sys
from signal import SIGINT, signal

import scapy.all as scapy
from scapy.layers import http
from termcolor import colored

CRED_KEYWORDS = ["login", "user", "pass", "mail", "pwd", "email", "username"]


class HTTPSniffer:
    def __init__(self, interface: str, keywords: list[str], verbose: bool = False):
        self.interface = interface
        self.keywords = [k.lower() for k in keywords]
        self.verbose = verbose

    def _extract_url(self, packet) -> str:
        req = packet[http.HTTPRequest]
        host = req.Host.decode(errors="ignore") if req.Host else ""
        path = req.Path.decode(errors="ignore") if req.Path else ""
        return f"http://{host}{path}"

    def _check_credentials(self, packet) -> None:
        if not packet.haslayer(scapy.Raw):
            return
        try:
            payload = packet[scapy.Raw].load.decode(errors="ignore")
        except Exception:
            return

        payload_lower = payload.lower()
        matched = [kw for kw in self.keywords if kw in payload_lower]
        if matched:
            print(
                colored(
                    f"[+] Possible credentials (matched: {', '.join(matched)}):\n    {payload}",
                    "green",
                )
            )

    def process_packet(self, packet) -> None:
        if not packet.haslayer(http.HTTPRequest):
            return

        url = self._extract_url(packet)
        print(colored(f"[!] URL visited: {url}", "yellow"))

        self._check_credentials(packet)

    def start(self) -> None:
        print(
            colored(
                f"[+] Sniffing HTTP traffic on interface '{self.interface}'", "cyan"
            )
        )
        try:
            scapy.sniff(iface=self.interface, prn=self.process_packet, store=False)
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
        description="Sniff HTTP requests and flag likely plaintext credentials on a given interface."
    )
    parser.add_argument(
        "-i",
        "--interface",
        required=True,
        help="Network interface to sniff on (e.g. eth0, ens33, wlan0)",
    )
    parser.add_argument(
        "-k",
        "--keywords",
        default=",".join(CRED_KEYWORDS),
        help=f"Comma-separated keywords to flag as possible credentials (default: {','.join(CRED_KEYWORDS)})",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show extra diagnostic output",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    def handle_sigint(signum, frame):
        print(colored("\n[!] Ctrl+C pressed. Exiting immediately...", "red"))
        sys.exit(1)

    signal(SIGINT, handle_sigint)

    sniffer = HTTPSniffer(
        interface=args.interface, keywords=keywords, verbose=args.verbose
    )
    sniffer.start()


if __name__ == "__main__":
    main()
