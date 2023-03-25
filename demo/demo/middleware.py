from django.urls import get_script_prefix

try:
    from urlparse.parse import urlparse
except ImportError:
    from urllib.parse import urlparse

from whitenoise.middleware import WhiteNoiseMiddleware
from whitenoise.string_utils import ensure_leading_trailing_slash


class WhiteNoiseMediaMiddleware(WhiteNoiseMiddleware):
    def configure_from_settings(self, settings):
        # Default configuration
        self.autorefresh = settings.DEBUG
        self.use_finders = settings.DEBUG
        self.static_prefix = urlparse(settings.MEDIA_URL or "").path
        script_prefix = get_script_prefix().rstrip("/")
        if script_prefix:
            if self.static_prefix.startswith(script_prefix):
                self.static_prefix = self.static_prefix[len(script_prefix) :]  # noqa
        if settings.DEBUG:
            self.max_age = 0
        # Allow settings to override default attributes
        for attr in self.config_attrs:
            settings_key = "WHITENOISE_{0}".format(attr.upper())
            try:
                value = getattr(settings, settings_key)
            except AttributeError:
                pass
            else:
                value = value
                setattr(self, attr, value)
        self.static_prefix = ensure_leading_trailing_slash(self.static_prefix)
        self.static_root = settings.MEDIA_ROOT
