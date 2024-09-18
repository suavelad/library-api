from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.conf import settings
from loguru import logger


EMAIL_FROM_ADDRESS="Library <support@library.co>"


def send_user_verification_email(payload):
    link = payload["link"]
    user_first_name = payload["user_first_name"]
    user_email = payload.get("user_email", None)

    data = {
        "link": link,
        "user_first_name": user_first_name if user_first_name else "",
    }

    message = get_template("verify-email-new.html").render(data)
    if not user_email:
        logger.error("No email found")
        return

    try:
        mail = EmailMessage(
            subject="User Verification",
            body=message,
            from_email=EMAIL_FROM_ADDRESS,
            to=[user_email],
            reply_to=[EMAIL_FROM_ADDRESS],
        )
        mail.content_subtype = "html"
        mail.send()

    except Exception as e:
        logger.error(e)
        return


def send_user_reset_password_email(payload):
    link = payload["url"]
    user_first_name = payload["name"]
    user_email = payload.get("email", None)

    data = {"link": link, "user_first_name": user_first_name if user_first_name else ""}

    message = get_template("reset-password.html").render(data)

    if not user_email:
        logger.error("No email found")
        return

    try:
        mail = EmailMessage(
            subject="User Password Reset",
            body=message,
            from_email=EMAIL_FROM_ADDRESS,
            to=[user_email],
            reply_to=[EMAIL_FROM_ADDRESS],
        )
        mail.content_subtype = "html"
        mail.send()

    except Exception as e:
        logger.error(e)
        return


def send_user_magic_login_email(payload):
    link = payload["link"]
    user_first_name = payload["name"]
    user_email = payload.get("user_email", None)
    text = payload["text"]

    data = {
        "link": link,
        "user_first_name": user_first_name if user_first_name else "",
        "message": text,
    }

    message = get_template("magic-login.html").render(data)

    if not user_email:
        logger.error("No email found")
        return

    try:
        mail = EmailMessage(
            subject="User Magic Login",
            body=message,
            from_email=EMAIL_FROM_ADDRESS,
            to=[user_email],
            reply_to=[EMAIL_FROM_ADDRESS],
        )
        mail.content_subtype = "html"
        mail.send()
    except Exception as e:
        logger.error(e)
        return
