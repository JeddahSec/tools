#!/usr/bin/env python3

import argparse
import re
import subprocess
import sys
from signal import SIGINT, signal

from termcolor import colored


def default_signal_handler(signum, frame):
    """Handle Ctrl+C by printing a message and exiting gracefully"""
    print(colored("\n[!] Ctrl+C pressed. Exiting immediately...", "red"))
    sys.exit(1)


# Handle Ctrl+C
signal(SIGINT, default_signal_handler)


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Tool to change the MAC address of a network interface (Requires Root/Sudo)"
    )
    parser.add_argument(
        "-i",
        "--interface",
        required=True,
        help="Network interface name (e.g., eth0, wlan0, ens33)",
    )
    parser.add_argument(
        "-m",
        "--mac",
        required=True,
        help="New MAC address (e.g., 00:11:22:33:44:55)",
    )

    return parser.parse_args()


def is_valid_input(interface, mac_address):
    # Matches common Linux interfaces: ethX, wlanX, enpXsX, ensX, etc.
    interface_pattern = r"^[a-zA-Z0-9._-]+$"
    # Case-insensitive MAC address validation
    mac_pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"

    is_valid_interface = re.match(interface_pattern, interface)
    is_valid_mac = re.match(mac_pattern, mac_address)

    return bool(is_valid_interface and is_valid_mac)


def change_mac_address(interface, mac_address):
    if not is_valid_input(interface, mac_address):
        print(colored("[-] Error: Invalid interface or MAC address format.", "red"))
        sys.exit(1)

    print(
        colored(
            f"[*] Attempting to change MAC address for {interface} to {mac_address}...",
            "cyan",
        )
    )

    try:
        # Using modern 'ip' command instead of deprecated 'ifconfig'
        # To use ifconfig instead, uncomment the commented lines below
        subprocess.run(["ip", "link", "set", interface, "down"], check=True)
        subprocess.run(
            ["ip", "link", "set", interface, "address", mac_address], check=True
        )
        subprocess.run(["ip", "link", "set", interface, "up"], check=True)

        # Legacy alternative if 'ip' is not available:
        # subprocess.run(["ifconfig", interface, "down"], check=True)
        # subprocess.run(["ifconfig", interface, "hw", "ether", mac_address], check=True)
        # subprocess.run(["ifconfig", interface, "up"], check=True)

        print(
            colored(
                f"\n[+] Successfully changed MAC address on {interface} to {mac_address}",
                "green",
            )
        )

    except subprocess.CalledProcessError as e:
        print(colored(f"\n[-] Failed to change MAC address.", "red"))
        print(
            colored(
                f"    Ensure you are running this script with sudo/root privileges.",
                "yellow",
            )
        )
    except FileNotFoundError:
        print(
            colored(
                "\n[-] Error: Required system utilities ('ip' or 'ifconfig') not found.",
                "red",
            )
        )


def main():
    args = get_arguments()
    change_mac_address(args.interface, args.mac)


if __name__ == "__main__":
    main()
