from unittest.mock import Mock, patch
from uuid import UUID

import pytest
from common.email.email_service import EmailService


@pytest.fixture
def smtp_client_mock():
    with patch("smtplib.SMTP_SSL") as smtp_mock:
        client_mock = Mock()
        smtp_mock.return_value.__enter__.return_value = client_mock
        yield client_mock


@pytest.mark.unit
def test_send_email_smtp(smtp_client_mock):
    uuid = UUID("4333cd05-72f4-4839-8185-f0227f7f4750")
    response = EmailService.send_email(
        smtp_config={},
        from_address="a@abc.com",
        recipients=["b@abc.com"],
        template_name="message_log",
        template_context_vars={"a": 1, "b": uuid},
    )
    smtp_client_mock.login.assert_called_once()
    smtp_client_mock.sendmail.assert_called_once()
