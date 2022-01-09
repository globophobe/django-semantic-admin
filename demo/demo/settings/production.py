import sentry_sdk
from decouple import config
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "https://semantic-admin-n673kvbdna-an.a.run.app/",
    "semantic-admin.com",
]

sentry_sdk.init(
    dsn=config("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    # Less transactions
    traces_sample_rate=0.01,
)

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
