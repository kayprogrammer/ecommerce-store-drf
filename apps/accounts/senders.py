from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import threading
from apps.accounts.models import User


class EmailThread(threading.Thread):
    """
    A class to handle email sending in a separate thread to avoid blocking the main thread.

    Attributes:
        email (EmailMessage): The email message to be sent.
    """

    def __init__(self, email: EmailMessage):
        """
        Initialize the EmailThread instance.

        Args:
            email (EmailMessage): The email message to be sent.
        """
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        """Send the email when the thread is run."""
        self.email.send()


class EmailUtil:
    """Utility class for sending different types of emails."""

    @staticmethod
    def send_welcome_email(user: User):
        """
        Send a welcome email to the user after account verification.

        Args:
            user (User): The user instance to whom the email is to be sent.
        """
        subject = "Account Verified"
        message = render_to_string(
            "accounts/welcome.html",
            {
                "domain": settings.FRONTEND_URL,
                "name": f"{user.first_name} {user.last_name}",
                "site_name": settings.SITE_NAME,
            },
        )

        email_message = EmailMessage(subject=subject, body=message, to=[user.email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def send_payment_failed_email(name: str, email: str, amount: float):
        """
        Send an email to notify the user of a failed payment.

        Args:
            name (str): The name of the recipient.
            email (str): The email address of the recipient.
            amount (float): The amount that failed to process.
        """
        if not email:
            return
        subject = "Payment Unverified"
        message = render_to_string(
            "shop/payment_failed_email.html",
            {
                "domain": settings.FRONTEND_URL,
                "name": name,
                "amount": amount,
                "site_name": settings.SITE_NAME,
            },
        )

        email_message = EmailMessage(subject=subject, body=message, to=[email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()

    @staticmethod
    def send_payment_success_email(name: str, email: str, amount: float):
        """
        Send an email to notify the user of a successful payment.

        Args:
            name (str): The name of the recipient.
            email (str): The email address of the recipient.
            amount (float): The amount that was successfully processed.
        """
        if not email:
            return
        subject = "Payment Verified"
        message = render_to_string(
            "shop/payment_success_email.html",
            {
                "domain": settings.FRONTEND_URL,
                "name": name,
                "amount": amount,
                "site_name": settings.SITE_NAME,
            },
        )

        email_message = EmailMessage(subject=subject, body=message, to=[email])
        email_message.content_subtype = "html"
        EmailThread(email_message).start()
