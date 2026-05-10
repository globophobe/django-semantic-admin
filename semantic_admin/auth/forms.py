from django.contrib.auth.forms import AdminPasswordChangeForm


class SemanticAdminPasswordChangeForm(AdminPasswordChangeForm):
    """Semantic admin password change form."""

    use_required_attribute = False
