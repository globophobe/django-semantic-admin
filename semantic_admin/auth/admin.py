from functools import wraps

from django.contrib import admin
from django.contrib.admin.exceptions import NotRegistered
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group, User

from semantic_admin.admin import SemanticModelAdmin
from semantic_admin.auth.forms import SemanticAdminPasswordChangeForm


class SemanticGroupAdmin(DjangoGroupAdmin, SemanticModelAdmin):
    """Semantic group admin."""

    filter_horizontal = ()


class SemanticUserAdmin(DjangoUserAdmin, SemanticModelAdmin):
    """Semantic user admin."""

    change_password_form = SemanticAdminPasswordChangeForm
    filter_horizontal = ()


def register_semantic_auth_admin(site: AdminSite | None = None) -> None:
    """Register semantic auth admin.

    Only register if UserAdmin and GroupAdmin are defaults. Do not register if
    custom admin or otherwise unregistered.
    """
    site = site or admin.site
    replacements = (
        (User, DjangoUserAdmin, SemanticUserAdmin),
        (Group, DjangoGroupAdmin, SemanticGroupAdmin),
    )

    for model, default_admin_class, semantic_admin_class in replacements:
        if model._meta.swapped:
            continue

        try:
            model_admin = site.get_model_admin(model)
        except NotRegistered:
            continue

        if model_admin.__class__ is not default_admin_class:
            continue

        site.unregister(model)
        site.register(model, semantic_admin_class)


def init_semantic_auth_admin() -> None:
    """Initialize semantic auth admin.

    semantic_admin appears before django.contrib.admin. This means 
    semantic_admin's app ready() runs before django.contrib.admin 
    imports auth.admin. Wrapping autodiscover gives us deterministic 
    post-autodiscover hook.
    """
    register_semantic_auth_admin()

    if getattr(admin.autodiscover, "_semantic_admin_auth_hook", False):
        return

    original_autodiscover = admin.autodiscover

    @wraps(original_autodiscover)
    def autodiscover_with_semantic_auth(*args, **kwargs):
        result = original_autodiscover(*args, **kwargs)
        register_semantic_auth_admin()
        return result

    autodiscover_with_semantic_auth._semantic_admin_auth_hook = True
    admin.autodiscover = autodiscover_with_semantic_auth
