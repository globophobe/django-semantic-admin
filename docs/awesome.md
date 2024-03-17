Awesome optional features
-------------------------

<ol><li>Optional integration with <a href="https://github.com/carltongibson/django-filter">django_filter</a>:</li></ol>

<img src="https://raw.githubusercontent.com/globophobe/django-semantic-admin/master/docs/screenshots/django-filter.png" width="335" alt="django-filter" />

To enable this awesome feature, also install [django-semantic-filter](https://github.com/globophobe/django-semantic-filter), and add `filterset_class` to your Django admin:

```python
from semantic_filter import SemanticFilterSet

class DemoFilter(SemanticFilterSet):
    class Meta:
        model = Demo
        fields = ("demo_field",)

class DemoAdmin(SemanticModelAdmin):
    filterset_class = DemoFilter
```

<ol start="2"><li>HTML preview in Django `autocomplete_fields`:</li></ol>

<img src="https://raw.githubusercontent.com/globophobe/django-semantic-admin/master/docs/screenshots/html5-autocomplete.png" width="670" alt="html5-autocomplete" />

To enable this awesome feature, add the `semantic_autocomplete` property to your Django model:

```python
class DemoModel(models.Model):
    @property
    def semantic_autocomplete(self):
        html = self.get_img()
        return format_html(html)
```

<ol start="3"><li>Optional integration with <a href="https://github.com/django-import-export/django-import-export">django-import-export</a>:</li></ol>

<img src="https://raw.githubusercontent.com/globophobe/django-semantic-admin/master/docs/screenshots/django-import-export.png" width="670" alt="django-import-export" />

To enable this awesome feature, instead of `import_export.ImportExportModelAdmin`, etc:

```python
from import_export.admin import ImportExportModelAdmin 

class ExampleImportExportAdmin(ImportExportModelAdmin):
    pass
```

Inherit from their `Semantic` equivalents:

```python
from semantic_admin.contrib.import_export.admin import SemanticImportExportModelAdmin

class ExampleImportExportAdmin(SemanticImportExportModelAdmin):
    pass
```
