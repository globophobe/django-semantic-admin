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
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path
from django.views.generic.base import RedirectView
from django.views.i18n import JavaScriptCatalog

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
    path("", admin.site.urls),
]
