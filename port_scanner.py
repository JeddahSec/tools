#!/usr/bin/env python3

import argparse
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from signal import SIGINT, signal

from termcolor import colored


def default_signal_handler(signum, frame):
    """Handle Ctrl+C by printing a message and exiting gracefully"""
    print(colored("\n[!] Ctrl+C pressed. Exiting immediately...", "red"))
    sys.exit(1)


# Handle Ctrl+C
signal(SIGINT, default_signal_handler)


def get_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="Simple Port Scanner")
    parser.add_argument(
        "-t",
        "--target",
        dest="target",
        help="Target host to scan (e.g., 192.168.1.1 or google.com)",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-p",
        "--port",
        dest="port",
        help="Port or range to scan (e.g., 80, 80-100, or 80,443)",
        type=str,
        default="1-1000",
    )
    args = parser.parse_args()
    return args.target, args.port


def parse_ports(port_input):
    """Parse port input string into a list of integers"""
    try:
        if "-" in port_input:
            start_port, end_port = map(int, port_input.split("-"))
            if not (0 <= start_port <= 65535 and 0 <= end_port <= 65535):
                raise ValueError
            return range(start_port, end_port + 1)
        elif "," in port_input:
            ports = [int(port.strip()) for port in port_input.split(",")]
            if any(not (0 <= p <= 65535) for p in ports):
                raise ValueError
            return ports

        port = int(port_input)
        if not (0 <= port <= 65535):
            raise ValueError
        return [port]
    except ValueError:
        print(
            colored(
                "[!] Invalid port format or out of range (0-65535). Use e.g. '80', '1-1000', or '80,443'",
                "red",
            )
        )
        sys.exit(1)


def port_scanner(target_ip, port, timeout=0.5):
    """Scan a single port and attempt simple banner grabbing if open"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            # 1. Check connection
            s.connect((target_ip, port))

            # 2. Attempt to grab raw response lines
            raw_response = ""
            try:
                raw_response = s.recv(1024).decode(errors="ignore").strip()
            except socket.timeout:
                try:
                    # Send proper double CRLF terminator for web servers
                    s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                    raw_response = s.recv(1024).decode(errors="ignore").strip()
                except (socket.timeout, OSError):
                    pass

            # 3. Parse and print output
            if raw_response:
                lines = [
                    line.strip() for line in raw_response.split("\n") if line.strip()
                ]
                primary_banner = lines[0]

                print(
                    colored(
                        f"[+] Port {port} is open | Banner: {primary_banner}", "green"
                    )
                )

                # Print additional lines of the banner if they exist, in "dark_grey"
                if len(lines) > 1:
                    for line in lines[1:5]:  # Limit output to first 5 lines
                        print(colored(f"    | {line}", "dark_grey"))
            else:
                print(colored(f"[+] Port {port} is open (No banner)", "green"))

    except (socket.timeout, ConnectionRefusedError, OSError):
        pass


def scan_ports(target_ip, ports):
    """Scan a list of ports concurrently while remaining responsive to interrupts"""
    print(colored(f"[*] Starting scan on target {target_ip}...", "magenta"))

    executor = ThreadPoolExecutor(max_workers=50)
    futures = []

    try:
        for port in ports:
            futures.append(executor.submit(port_scanner, target_ip, port))

        for future in as_completed(futures):
            future.result()

    except KeyboardInterrupt:
        print(colored("\n[!] Scan aborted by user.", "red"))
        executor.shutdown(wait=False, cancel_futures=True)
        sys.exit(1)
    finally:
        executor.shutdown(wait=True)


def main():
    """Main Function"""
    target, port_input = get_arguments()

    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(colored(f"[!] Could not resolve hostname: {target}", "red"))
        sys.exit(1)

    ports = parse_ports(port_input)
    scan_ports(target_ip, ports)


if __name__ == "__main__":
    main()
