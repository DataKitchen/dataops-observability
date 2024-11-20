__all__ = ["EmailService"]

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from collections.abc import Mapping

from common.email.email_renderer import HandlebarsEmailRenderer
from conf import settings

LOG = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    def send_email(
        smtp_config: dict,
        from_address: str | None,
        recipients: list[str],
        template_name: str,
        template_context_vars: Mapping,
    ) -> dict:
        try:
            from_address = from_address or settings.SMTP["from_address"]
            content, subject = HandlebarsEmailRenderer.render(template_name, template_context_vars)
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = from_address
            message["To"] = ", ".join(recipients)
            mime = MIMEText(content, "html")
            message.attach(mime)
            with smtplib.SMTP_SSL(
                host=smtp_config.get("endpoint") or settings.SMTP["endpoint"],
                port=smtp_config.get("port") or settings.SMTP["port"],
                context=context,
            ) as smtp_server:
                smtp_server.login(
                    smtp_config.get("username") or settings.SMTP["username"],
                    smtp_config.get("password") or settings.SMTP["password"],
                )
                response = smtp_server.sendmail(from_address, recipients, message.as_string())
        except Exception:
            LOG.exception("Failed to send Email")
            raise
        else:
            LOG.info("Email Sent")
            return response
