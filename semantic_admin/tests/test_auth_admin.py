from unittest.mock import patch

from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase, override_settings
from django.urls import path, reverse

from semantic_admin.auth.admin import (
    SemanticGroupAdmin,
    SemanticUserAdmin,
    register_semantic_auth_admin,
)
from semantic_admin.auth.forms import SemanticAdminPasswordChangeForm
from semantic_forms import SemanticModelMultipleChoiceField
from semantic_forms.widgets import SemanticSelectMultiple

user_admin_site = AdminSite(name="admin")
user_admin_site.register(get_user_model(), SemanticUserAdmin)
urlpatterns = [path("", user_admin_site.urls)]


class CustomUserAdmin(UserAdmin):
    pass


class AuthAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )

    def setUp(self):
        super().setUp()
        self.admin_site = AdminSite()
        self.request_factory = RequestFactory()
        self.client.force_login(self.user)

    @override_settings(ROOT_URLCONF=__name__)
    def test_user_password_change_uses_semantic_form(self):
        with patch(
            "semantic_admin.templatetags.semantic_app_list.get_admin_site",
            return_value=user_admin_site,
        ):
            response = self.client.get(
                reverse("admin:auth_user_password_change", args=(self.user.pk,))
            )

        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('class="ui large breadcrumb"', content)
        self.assertIn('class="ui form"', content)
        self.assertIn('class="ui segment"', content)
        self.assertIn('id="id_usable_password"', content)
        self.assertIn('name="set-password"', content)
        self.assertIn('name="unset-password"', content)
        self.assertRegex(content, r'<form class="ui form"')
        self.assertNotIn("novalidate", content)
        self.assertNotIn('class="breadcrumbs"', content)

    def test_default_auth_admin_is_reregistered_as_semantic_admin(self):
        user_model = get_user_model()
        self.admin_site.register(user_model, UserAdmin)
        self.admin_site.register(Group, GroupAdmin)

        register_semantic_auth_admin(self.admin_site)

        user_admin = self.admin_site.get_model_admin(user_model)
        group_admin = self.admin_site.get_model_admin(Group)

        self.assertIsInstance(user_admin, SemanticUserAdmin)
        self.assertIsInstance(group_admin, SemanticGroupAdmin)
        self.assertEqual(user_admin.filter_horizontal, ())
        self.assertEqual(group_admin.filter_horizontal, ())
        self.assertIs(
            user_admin.change_password_form,
            SemanticAdminPasswordChangeForm,
        )

    def test_semantic_auth_admin_uses_semantic_model_multiple_choice_fields(self):
        request = self.request_factory.get("/")
        request.user = self.user
        user_model = get_user_model()
        self.admin_site.register(user_model, SemanticUserAdmin)
        self.admin_site.register(Group, SemanticGroupAdmin)

        user_form = self.admin_site.get_model_admin(user_model).get_form(
            request,
            self.user,
        )
        group_form = self.admin_site.get_model_admin(Group).get_form(
            request,
            Group(),
        )

        for field_name in ("groups", "user_permissions"):
            field = user_form.base_fields[field_name]
            self.assertIsInstance(field, SemanticModelMultipleChoiceField)
            self.assertIsInstance(field.widget.widget, SemanticSelectMultiple)

        permissions = group_form.base_fields["permissions"]
        self.assertIsInstance(permissions, SemanticModelMultipleChoiceField)
        self.assertIsInstance(permissions.widget.widget, SemanticSelectMultiple)

    def test_custom_auth_admin_is_not_replaced(self):
        user_model = get_user_model()
        self.admin_site.register(user_model, CustomUserAdmin)
        self.admin_site.register(Group, ModelAdmin)

        register_semantic_auth_admin(self.admin_site)

        self.assertIsInstance(
            self.admin_site.get_model_admin(user_model),
            CustomUserAdmin,
        )
        self.assertIs(
            self.admin_site.get_model_admin(Group).__class__,
            ModelAdmin,
        )

    def test_unregistered_auth_models_are_left_unregistered(self):
        register_semantic_auth_admin(self.admin_site)

        self.assertFalse(self.admin_site.is_registered(get_user_model()))
        self.assertFalse(self.admin_site.is_registered(Group))
