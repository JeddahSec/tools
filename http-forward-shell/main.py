#!/usr/bin/env python3
"""
Entry point for ForwardShell.

Usage::

    python3 main.py                                  # default localhost
    python3 main.py -u http://10.10.10.1/index.php   # custom target
"""

import sys
from argparse import ArgumentParser, Namespace
from signal import SIGINT, signal
from types import FrameType
from typing import Optional

from termcolor import colored

from forwardshell import DEFAULT_URL, ForwardShell


def parse_args() -> Namespace:
    """Parse command-line arguments."""
    parser = ArgumentParser(
        description="HTTP-based forward shell client.",
        epilog="Example: python3 main.py -u http://10.10.10.1/index.php",
    )
    parser.add_argument(
        "-u",
        "--url",
        default=DEFAULT_URL,
        metavar="URL",
        help=f"Target PHP endpoint (default: {DEFAULT_URL})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    shell = ForwardShell(url=args.url)

    def handle_sigint(signum: int, frame: Optional[FrameType]) -> None:
        """Clean up remote files and exit on Ctrl+C."""
        print(colored("\n[!] Ctrl+C detected. Cleaning up and exiting…", "red"))
        shell.remove_data()
        sys.exit(1)

    signal(SIGINT, handle_sigint)
    shell.run()
