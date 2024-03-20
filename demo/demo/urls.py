"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import re

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve
from semantic_forms.docs.views import semantic_forms_kitchen_sink

from demo.forms import LoginForm

urlpatterns = [
    path(
        "login/",
        LoginView.as_view(authentication_form=LoginForm),
    ),
    path(
        "password_change/",
        RedirectView.as_view(url="/"),
        name="change-password-redirect",
    ),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    re_path(
        r"^%s(?P<path>.*)$" % re.escape(settings.MEDIA_URL.lstrip("/")),
        serve,
        kwargs={"document_root": settings.MEDIA_ROOT},
    ),
    path("forms/", semantic_forms_kitchen_sink, name="semantic-forms-kitchen-sink"),
    path("", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns.insert(0, path("__debug__/", include("debug_toolbar.urls")))
