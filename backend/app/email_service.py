import logging
import smtplib
from email.message import EmailMessage
from .config import get_settings

outbox: list[dict[str, str]] = []

def send_reset_email(address: str, url: str):
    settings = get_settings()
    if settings.email_provider == "memory":
        outbox.append({"to": address, "url": url})
        return
    message = EmailMessage()
    message["Subject"] = "Restablece tu contraseña de QuickShop"
    message["From"] = settings.email_from
    message["To"] = address
    message.set_content(f"Has solicitado cambiar tu contraseña. Este enlace caduca en {settings.reset_minutes} minutos y solo funciona una vez.\n\n{url}\n\nSi no has sido tú, puedes ignorar este mensaje.")
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            if settings.smtp_starttls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password.get_secret_value())
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException):
        logging.getLogger(__name__).error("No se pudo entregar el correo de recuperación; revisar el proveedor SMTP.")
