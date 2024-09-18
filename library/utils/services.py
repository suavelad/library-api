from django.core.mail import send_mail
from django.conf import settings


def send_sms(user, message_to_send, phone_number):
    pass


def send_email(subject, message, email):
    from_email = settings.EMAIL_HOST_USER
    to_email = [email]
    send_mail(subject, message, from_email, to_email, fail_silently=False)
    return "Email sent"
