import pyotp
import base64
import jwt
import re

from rest_framework_simplejwt.backends import TokenBackend
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import Q

from rest_framework_jwt.settings import api_settings
from library.utils import generateKey

from loguru import logger

User = get_user_model()


def generate_otp(contact, verification=False):
    keygen = generateKey()
    key = base64.b32encode(keygen.returnValue(contact).encode())

    if verification == True:
        hotp = pyotp.HOTP(key)
        user = User.objects.filter(Q(email=contact) | Q(phone=contact)).first()
        otp_data = hotp.at(int(user.id))
        return otp_data

    OTP = pyotp.TOTP(key, interval=settings.PASSWORD_OTP_TIMEOUT)
    otp_data = OTP.now()

    return otp_data


def generate_magic_link_otp(contact):
    keygen = generateKey()
    key = base64.b32encode(keygen.returnValue(contact).encode())

    OTP = pyotp.TOTP(key, interval=settings.MAGIC_LINK_OTP_TIMEOUT)
    otp_data = OTP.now()

    return otp_data


def generate_token(user):
    from ..serializers import UserSerializer

    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user)

    the_serializer = UserSerializer

    user_data = the_serializer(user).data
    payload["user_info"] = user_data
    payload["email"] = user.email
    token = jwt.encode(payload, key=settings.SECRET_KEY, algorithm="HS256")

    return token


def is_contain_special_characters(name):
    formatted_name = re.search(r"[^a-zA-Z0-9()$%_]", name)
    return True if formatted_name else False


def get_user_with_token(token):
    User = get_user_model()

    try:
        valid_data = TokenBackend(algorithm="HS256").decode(token, verify=False)
        user_id = valid_data["user_id"]
        user = User.objects.get(id=user_id)
        return user
    except Exception as e:
        logger.error(f"failed {e}")
        return None
