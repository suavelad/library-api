from django.conf import settings
from decouple import config


ENV_MODE = settings.ENV



# For URLS
FRONTEND_RESET_URL = config("FRONTEND_RESET_URL")
FRONTEND_VERIFY_URL = config("FRONTEND_VERIFY_URL")
FRONTEND_VERIFY_MAGIC_LOGIN_URL = config("FRONTEND_VERIFY_MAGIC_LOGIN_URL")
