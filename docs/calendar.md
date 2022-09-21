Translating the calendar
-----

`SemanticModelAdmin`, `SemanticStackedInline`, and `SemanticTabularInline` admin classes for models with `DateTimeField`, `DateField`, or `TimeField` will automatically use Semantic UI's calendar component. 

To translate the calendar add Django's `JavaScriptCatalog` to `urlpatterns`, as described in Django's [Translation documentation](https://docs.djangoproject.com/en/4.0/topics/i18n/translation/#module-django.views.i18n).
