A Django Semantic UI Admin theme
--------------------------------
Django [Semantic UI](https://semantic-ui.com/) Admin is a completely free (MIT) admin theme for Django. Actually, this is my 3rd admin theme for Django. The first was forgettable, and the second was with Pure CSS. Pure CSS was great, but lacked JavaScript components.

Semantic UI looks professional, and has great JavaScript components.

Why?
----
* Looks professional, with a nice sidebar.
* Resonsive design, even [tables can stack](https://semantic-ui.com/collections/table.html#stacking) responsively on mobile.
* JavaScript datepicker and timepicker components.
* JavaScript selects, including multiple selections, which integrate well with Django autocomplete fields.
* Semantic UI has libraries for [React](https://react.semantic-ui.com/) and [Vue](https://semantic-ui-vue.github.io/#/), in addition to jQuery. This means this package can be used to style the admin, and custom views can be added with React or Vue components with the same style.

Install
-------

Install from PyPI:

```
pip install django-semantic-admin
```

Add to `settings.py` before `django.contrib.admin`:

```
INSTALLED_APPS = [
  "semantic_admin",
  "django.contrib.admin",
  ...
]
```

Usage
-----

Instead of `admin.ModelAdmin`, `admin.StackedInline`, or `admin.TabularInline`:

```
class ExampleStackedInline(admin.StackedInline):
  pass

class ExampleTabularInline(admin.TabularInline):
  pass

class ExampleAdmin(admin.ModelAdmin):
  inlines = (ExampleStackedInline, ExampleTabularInline)
```

Inherit from their `Semantic` equivalents:

```
from semantic_admin import SemanticModelAdmin, SemanticStackedInline, SemanticTabularInline

class ExampleStackedInline(SemanticStackedInline):
  pass

class ExampleTabularInline(SemanticTabularInline):
  pass

class ExampleAdmin(SemanticModelAdmin):
  inlines = (ExampleStackedInline, ExampleTabularInline)
```

Notes
-----
Please note, this package uses [Fomantic UI](https://fomantic-ui.com/) the official community fork of Semantic UI.
