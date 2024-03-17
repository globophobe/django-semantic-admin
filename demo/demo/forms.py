from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import UsernameField
from django.utils.html import format_html

try:
    from django.utils.translation import gettext_lazy as _  # Django >= 4
except ImportError:
    from django.utils.translation import ugettext_lazy as _


class LoginForm(AdminAuthenticationForm):
    """Login form."""

    error_messages = {
        **AdminAuthenticationForm.error_messages,
        "invalid_login": format_html(
            _("Please enter username <i>admin</i> and password <i>semantic</i>.")
        ),
    }

    username = UsernameField(
        widget=forms.TextInput(attrs={"placeholder": "admin", "autofocus": True})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "semantic"}),
    )
