# tools

🛠️ A collection of Python-based network utilities for scanning, sniffing, and manipulating network traffic. Originally part of [JeddahSec/dotfiles](https://github.com/JeddahSec/dotfiles), now maintained as a standalone repo.

## Contents

| Script | Description |
|---|---|
| `arp_scan.py` | Scans the local network for active hosts using ARP requests |
| `arp_spoof.py` | Performs ARP spoofing / cache poisoning between hosts |
| `dns_sniffer.py` | Captures and inspects DNS traffic on the network |
| `http_sniffer.py` | Captures and inspects HTTP traffic on the network |
| `icmp_scanner.py` | Discovers live hosts using ICMP (ping) requests |
| `macchanger.py` | Changes the MAC address of a network interface |
| `port_scanner.py` | Scans a target host for open TCP ports |

## Requirements

- Python 3.x
- Root/administrator privileges (required for raw sockets, packet sniffing, and interface changes)
- Common packet libraries depending on script, e.g.:
  ```bash
  pip install scapy
  ```

## Usage

Each script can be run directly, typically with root privileges:

```bash
sudo python3 arp_scan.py
sudo python3 port_scanner.py <target-ip>
```

> Check each script's `--help` flag or source for specific arguments and options.

## ⚠️ Disclaimer

These tools interact directly with network traffic and can disrupt, intercept, or compromise systems on a network. They are intended **only** for:

- Authorized penetration testing
- Personal lab / homelab environments
- Educational and learning purposes

**Do not** use these tools against networks or devices you do not own or do not have explicit written permission to test. Unauthorized use of ARP spoofing, packet sniffing, or scanning tools may be illegal in your jurisdiction. The author assumes no liability for misuse.

## License

Provided as-is for educational and authorized security testing purposes. No warranty provided — use at your own risk.
