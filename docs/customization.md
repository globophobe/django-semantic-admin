
App list ordering
-----

Ordering of sidebar, and index page, apps and models can be customized with the optional `SEMANTIC_APP_LIST` setting.

With the following in settings.py, `app_2` will be displayed before `app_1`

```python
SEMANTIC_APP_LIST = [{ "app_label": "app_2" }, { "app_label": "app_1" }]
```


In this example, `ModelB` will be displayed before `ModelA`

```python
SEMANTIC_APP_LIST = [
    {
        "app_label": "app_1",
        "models": [{"object_name": "ModelB"}, {"object_name": "ModelA"}],
    },
]
```

Changing the logo
-----

The logo may be changed by overriding `menu.html`

<img src="https://raw.githubusercontent.com/globophobe/django-semantic-admin/master/docs/screenshots/pony-powered.png" alt="pony-powered" />

<ol><li>Add a dir to the <code>TEMPLATES</code> setting</li></ol>

```python
"DIRS": [BASE_DIR / "templates"],
```

<ol start="2"><li>Create a file <code>templates/admin/menu.html</code> with the following</li></ol>

```html
{% extends 'admin/menu.html' %}
{% block branding %}
<a class="item" href="{% url 'admin:index' %}">
  <img 
    title="Magic! Ponies! Django! Whee!" 
    src="http://media.djangopony.com/img/small/badge.png" 
    alt="{{ site_header|default:_('Django administration') }}" />
</a>
{% endblock %}
```

Customizing the CSS
-----

CSS may be customized by overriding `base.html`. 

<ol><li>Add a dir to the <code>TEMPLATES</code> setting</li></ol>

```python
"DIRS": [BASE_DIR / "templates"],
```

<ol start="2"><li>Create a file <code>templates/admin/base.html</code> with the following</li></ol>

```html
{% extends 'admin/base.html' %}
{% load static %}
{% block extrastyle %}
<link rel="stylesheet" href="{% static "demo_app/custom.css" %}" />
{% endblock %}
```

Translating the calendar
-----

`SemanticModelAdmin`, `SemanticStackedInline`, and `SemanticTabularInline` admin classes for models with `DateTimeField`, `DateField`, or `TimeField` will automatically use Semantic UI's calendar component. 

To translate the calendar add Django's `JavaScriptCatalog` to `urlpatterns`, as described in Django's [Translation documentation](https://docs.djangoproject.com/en/4.0/topics/i18n/translation/#module-django.views.i18n).
