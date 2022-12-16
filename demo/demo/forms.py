from django import forms
from django.utils.html import format_html
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import UsernameField

try:
    from django.utils.translation import gettext_lazy as _  # Django >= 4
except ImportError:
    from django.utils.translation import ugettext_lazy as _


class LoginForm(AdminAuthenticationForm):

    error_messages = {
        **AdminAuthenticationForm.error_messages,
        "invalid_login": format_html(_(
            "Please enter username <i>django</i> and password <i>semantic-admin</i>."
        )),
    }

    username = UsernameField(
        widget=forms.TextInput(attrs={"placeholder": "django", "autofocus": True})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "semantic-admin"}),
    )
