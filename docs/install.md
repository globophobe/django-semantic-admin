Install
-------

Install from PyPI:

```
pip install django-semantic-admin
```

Add to `settings.py` before `django.contrib.admin`:

```python
INSTALLED_APPS = [
    "semantic_admin",
    "django.contrib.admin",
    ...
]
```

Please remember to run `python manage.py collectstatic` for production deployments.

Usage
-----

Instead of `admin.ModelAdmin`, `admin.StackedInline`, or `admin.TabularInline`:

```python
class ExampleStackedInline(admin.StackedInline):
    pass

class ExampleTabularInline(admin.TabularInline):
    pass

class ExampleAdmin(admin.ModelAdmin):
    inlines = (ExampleStackedInline, ExampleTabularInline)
```

Inherit from their `Semantic` equivalents:

```python
from semantic_admin import SemanticModelAdmin, SemanticStackedInline, SemanticTabularInline

class ExampleStackedInline(SemanticStackedInline):
    pass

class ExampleTabularInline(SemanticTabularInline):
    pass

class ExampleAdmin(SemanticModelAdmin):
    inlines = (ExampleStackedInline, ExampleTabularInline)
```

