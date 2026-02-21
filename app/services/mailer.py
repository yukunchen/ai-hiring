"""Email sending service using SMTP."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from app.config import config


class EmailSender:
    """SMTP email sender service."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_name: Optional[str] = None,
    ):
        """Initialize email sender.

        Args:
            host: SMTP server host
            port: SMTP server port
            username: SMTP username
            password: SMTP password
            from_name: Sender display name
        """
        smtp_config = config.smtp
        self.host = host or smtp_config.get("host", "")
        self.port = port or smtp_config.get("port", 587)
        self.username = username or smtp_config.get("username", "")
        self.password = password or smtp_config.get("password", "")
        self.from_name = from_name or smtp_config.get("from_name", "HR Team")

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> dict:
        """Send email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body content
            html: Whether body is HTML

        Returns:
            Result dict with status and message
        """
        if not self.host or not self.username:
            return {
                "success": False,
                "error": "SMTP not configured",
            }

        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{self.from_name} <{self.username}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg["Date"] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")

            # Attach body
            mime_type = "html" if html else "plain"
            msg.attach(MIMEText(body, mime_type, "utf-8"))

            # Connect and send
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return {
                "success": True,
                "message": "Email sent successfully",
            }

        except smtplib.SMTPException as e:
            return {
                "success": False,
                "error": f"SMTP error: {str(e)}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send email: {str(e)}",
            }

    def send_email_to_multiple(
        self,
        to_emails: list[str],
        subject: str,
        body: str,
        html: bool = False,
    ) -> dict:
        """Send email to multiple recipients.

        Args:
            to_emails: List of recipient emails
            subject: Email subject
            body: Email body
            html: Whether body is HTML

        Returns:
            Result dict
        """
        if not to_emails:
            return {
                "success": False,
                "error": "No recipients specified",
            }

        results = []
        for email in to_emails:
            result = self.send_email(email, subject, body, html)
            results.append({"email": email, "result": result})

        all_success = all(r["result"]["success"] for r in results)

        return {
            "success": all_success,
            "results": results,
        }


# Singleton instance
_email_sender = None


def get_email_sender() -> EmailSender:
    """Get singleton email sender."""
    global _email_sender
    if _email_sender is None:
        _email_sender = EmailSender()
    return _email_sender
