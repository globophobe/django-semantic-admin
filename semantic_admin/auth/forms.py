from django import forms
from django.contrib.admin.forms import (
    AdminAuthenticationForm,
    AdminPasswordChangeForm as AdminSitePasswordChangeForm,
)
from django.contrib.auth.forms import (
    AdminPasswordChangeForm as AuthAdminPasswordChangeForm,
    PasswordResetForm,
)
from django.utils.translation import gettext_lazy as _


class SemanticAdminAuthenticationForm(AdminAuthenticationForm):
    """Semantic admin login form."""

    use_required_attribute = False


class SemanticAdminPasswordChangeForm(AuthAdminPasswordChangeForm):
    """Semantic user admin password change form."""

    use_required_attribute = False


class SemanticAdminSitePasswordChangeForm(AdminSitePasswordChangeForm):
    """Semantic admin site password change form."""

    use_required_attribute = False


class SemanticPasswordResetForm(PasswordResetForm):
    """Semantic password reset form."""

    use_required_attribute = False
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.TextInput(attrs={"autocomplete": "email"}),
    )
