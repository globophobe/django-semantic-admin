from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DemoAppConfig(AppConfig):
    """Demo App Config."""

    name = "demo_app"
    verbose_name = _("demo")
