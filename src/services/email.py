import smtplib
from email.message import EmailMessage

from config import BaseAppSettings


def send_email(settings: BaseAppSettings, to_email: str, subject: str, body: str) -> None:
    if not getattr(settings, "SMTP_HOST", None):
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USERNAME:
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        server.send_message(msg)


def send_activation_email(settings: BaseAppSettings, to_email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL.rstrip('/')}/activate?email={to_email}&token={token}"
    send_email(settings, to_email, "Activate your account", f"Activation link: {link}")


def send_password_reset_email(settings: BaseAppSettings, to_email: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL.rstrip('/')}/reset-password?email={to_email}&token={token}"
    send_email(settings, to_email, "Reset your password", f"Password reset link: {link}")