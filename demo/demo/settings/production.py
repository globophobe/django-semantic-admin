import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
SECRET_KEY = os.environ["SECRET_KEY"]

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "https://semantic-admin-n673kvbdna-an.a.run.app/",
    "semantic-admin.com",
]

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)

STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
