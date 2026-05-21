from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth.forms import AdminPasswordChangeForm


class SemanticAdminAuthenticationForm(AdminAuthenticationForm):
    """Semantic admin login form."""

    use_required_attribute = False


class SemanticAdminPasswordChangeForm(AdminPasswordChangeForm):
    """Semantic admin password change form."""

    use_required_attribute = False
