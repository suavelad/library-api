import sentry_sdk
from loguru import logger
from sentry_sdk.integrations.django import DjangoIntegration
from django.conf import settings

# from google.cloud.logging.handlers import CloudLoggingHandler
ENV_ENUM = settings.ENV_ENUM

if settings.ENV != ENV_ENUM.DEV:
    # if settings.ENV == "local":
    sentry_sdk.init(
        # dsn="https://ec782c389a944b4ead35388def06ed21@o4505193219424256.ingest.sentry.io/4505193278865408", # USE A NEW SENTRY LOG
        integrations=[DjangoIntegration()],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        environment=settings.ENV,
    )

LOGGING_CONFIG = None

ADMINS = [("Sunday", "sunnexajayi@gmail.com")]
