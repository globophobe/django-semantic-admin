Translating the calendar
-----

`SemanticModelAdmin`, `SemanticStackedInline`, and `SemanticTabularInline` admin classes for models with `DateTimeField`, `DateField`, or `TimeField` will automatically use Semantic UI's calendar component. 

To translate the calendar add Django's `JavaScriptCatalog` to `urlpatterns`, as described in Django's [Translation documentation](https://docs.djangoproject.com/en/4.0/topics/i18n/translation/#module-django.views.i18n).

To format the date, there is a setting using [Intl.DateTimeFormat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat) options.

Django Semantic Admin's default setting in `SEMANTIC_CALENDAR_OPTIONS` in `settings.py`

```python
SEMANTIC_CALENDAR_OPTIONS = {
    "datetime": {
        "intlDateTimeFormatOptions": {"dateStyle": "short", "timeStyle": "short"},
    },
    "date": {"intlDateTimeFormatOptions": {"dateStyle": "short"}},
    "time": {"intlDateTimeFormatOptions": {"timeStyle": "short"}},
}
```

A number of calendar options that can be serialized to JSON are supported. For example, as described in the Fomantic UI's [Calendar documentation](https://fomantic-ui.com/modules/calendar.html#24-hour-format), to additionally not display `AM/PM`.

```python
SEMANTIC_CALENDAR_OPTIONS = {
    "datetime": {
        "intlDateTimeFormatOptions": {"dateStyle": "short", "timeStyle": "short"},
        "ampm": False,
    },
    "date": {"intlDateTimeFormatOptions": {"dateStyle": "short"}},
    "time": {"intlDateTimeFormatOptions": {"timeStyle": "short"}, "ampm": False},
}
```
