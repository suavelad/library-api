"""
This is a django-split-settings main file.
For more information, read this:
https://github.com/sobolevn/django-split-settings

To change settings file:
'DJANGO_ENV=production python manage.py runserver
"""

from split_settings.tools import include, optional
from decouple import config


class ENV_ENUM:
    PRODUCTION = "production"
    STAGING = "staging"
    DEV = "dev"


ENV = config("ENV_MODE", ENV_ENUM.PRODUCTION)


base_settings = [
    "components/common.py",  # standard django settings
    # "components/redis.py",
    # "components/django_q.py",
    # "components/channels.py",
    "components/config_urls.py",
    "components/constants.py",
    "components/logger.py",
    "components/email_service.py",
    optional("environments/%s.py" % ENV),
]

include(*base_settings)
