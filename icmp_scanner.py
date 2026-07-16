#!/usr/bin/env python3

import argparse
import ipaddress
import platform
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from signal import SIGINT, signal

from termcolor import colored


def default_signal_handler(signum, frame):
    print(colored("\n[!] Ctrl+C pressed. Exiting immediately...", "red"))
    sys.exit(1)


signal(SIGINT, default_signal_handler)


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Fast multithreaded tool for discovering active hosts on a network (ICMP)"
    )
    parser.add_argument(
        "-t",
        "--target",
        required=True,
        help="Target IP (e.g. 192.168.1.1), Range (e.g. 192.168.1.1-50), or CIDR (e.g. 192.168.1.0/24)",
    )
    args = parser.parse_args()
    return args.target


def parse_target(target_str):
    """
    Parses various IP formats: single IP, CIDR block, or custom dash range.
    Returns a list of IP address strings.
    """
    targets = []
    target_str = target_str.strip()

    # Case 1: CIDR Notation (e.g., 192.168.1.0/24)
    if "/" in target_str:
        try:
            network = ipaddress.ip_network(target_str, strict=False)
            # hosts() excludes the network address (.0) and broadcast address (.255)
            return [str(ip) for ip in network.hosts()]
        except ValueError:
            pass

    # Case 2: Custom Dash Range in the last octet (e.g., 192.168.1.1-15)
    elif "-" in target_str:
        try:
            octets = target_str.split(".")
            if len(octets) == 4 and "-" in octets[3]:
                first_three_octets = ".".join(octets[:3])
                start_str, end_str = octets[3].split("-")
                start, end = int(start_str), int(end_str)

                if 0 <= start <= 255 and 0 <= end <= 255 and start <= end:
                    return [f"{first_three_octets}.{i}" for i in range(start, end + 1)]
        except ValueError:
            pass

    # Case 3: Single IP address
    else:
        try:
            ipaddress.ip_address(target_str)
            return [target_str]
        except ValueError:
            pass

    # If all parsing attempts fail
    print(
        colored(f"[!] Error: '{target_str}' is not a valid IP, CIDR, or range.", "red")
    )
    sys.exit(1)


def host_discovery(target):
    # Detect host OS to run correct ping command parameters
    param = "-n" if platform.system().lower() == "windows" else "-c"

    try:
        # Run ping; standard and error outputs are suppressed
        ping_process = subprocess.run(
            ["ping", param, "1", target],
            timeout=1,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if ping_process.returncode == 0:
            print(colored(f"\t[i] The IP {target} is active", "green"))
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass


def main():
    target_str = get_arguments()
    targets = parse_target(target_str)

    if not targets:
        print(colored("[!] No valid targets to scan.", "yellow"))
        sys.exit(1)

    print(
        colored(f"[+] Scanning {len(targets)} targets for active hosts...", "magenta")
    )

    max_threads = 100
    # Adjusted to not spawn more threads than actual targets to scan
    workers = min(max_threads, len(targets))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(host_discovery, targets)


if __name__ == "__main__":
    main()
