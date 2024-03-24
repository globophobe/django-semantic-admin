import datetime
import decimal
import json
from typing import Any

from django.contrib.admin.utils import display_for_value
from django.db import models
from django.forms import Field
from django.utils import formats, timezone
from django.utils.html import format_html

try:
    from django.contrib.postgres.fields import JSONField
except ImportError:
    from django.db.models import JSONField  # type: ignore


def semantic_display_for_field(
    value: Any, field: Field, empty_value_display: str
) -> str:
    """Semantic display for field"""
    from .templatetags.semantic_admin_list import _semantic_boolean_icon

    if getattr(field, "flatchoices", None):
        return dict(field.flatchoices).get(value, empty_value_display)
    # BooleanField needs special-case null-handling, so it comes before the
    # general null test.

    # BEGIN CUSTOMIZATION
    elif isinstance(field, models.BooleanField):
        return _semantic_boolean_icon(value)
    # END CUSTOMIZATION

    elif value is None:
        return empty_value_display
    elif isinstance(field, models.DateTimeField):
        return formats.localize(timezone.template_localtime(value))
    elif isinstance(field, (models.DateField, models.TimeField)):
        return formats.localize(value)
    elif isinstance(field, models.DecimalField):
        return formats.number_format(value, field.decimal_places)
    elif isinstance(field, (models.IntegerField, models.FloatField)):
        return formats.number_format(value)
    elif isinstance(field, models.FileField) and value:
        return format_html('<a href="{}">{}</a>', value.url, value)
    elif isinstance(field, JSONField) and value:
        try:
            return json.dumps(value, ensure_ascii=False, cls=field.encoder)
        except TypeError:
            return display_for_value(value, empty_value_display)
    else:
        return display_for_value(value, empty_value_display)


def semantic_display_for_value(
    value: Any, empty_value_display: str, boolean: bool = False
) -> str:
    """Semantic display for value"""
    from .templatetags.semantic_admin_list import _semantic_boolean_icon

    # BEGIN CUSTOMIZATION
    if boolean:
        return _semantic_boolean_icon(value)
    # END CUSTOMIZATION

    elif value is None:
        return empty_value_display
    elif isinstance(value, bool):
        return str(value)
    elif isinstance(value, datetime.datetime):
        return formats.localize(timezone.template_localtime(value))
    elif isinstance(value, (datetime.date, datetime.time)):
        return formats.localize(value)
    elif isinstance(value, (int, decimal.Decimal, float)):
        return formats.number_format(value)
    elif isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    else:
        return str(value)
