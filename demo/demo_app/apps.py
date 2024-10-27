from django.apps import AppConfig

try:
    from django.utils.translation import gettext_lazy as _  # Django >= 4
except ImportError:
    from django.utils.translation import ugettext_lazy as _


class DemoAppConfig(AppConfig):
    """Demo App Config."""

    name = "demo_app"
    verbose_name = _("demo")
