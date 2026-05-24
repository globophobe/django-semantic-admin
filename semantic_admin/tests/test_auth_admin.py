from unittest.mock import patch

from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model, views as auth_views
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.test import RequestFactory, TestCase, override_settings
from django.urls import path, reverse

from semantic_admin.auth.admin import (
    SemanticGroupAdmin,
    SemanticUserAdmin,
    register_semantic_auth_admin,
    register_semantic_password_change_form,
)
from semantic_admin.auth.forms import (
    SemanticAdminPasswordChangeForm,
    SemanticAdminSitePasswordChangeForm,
    SemanticPasswordResetForm,
)
from semantic_forms import SemanticModelMultipleChoiceField
from semantic_forms.widgets import SemanticSelectMultiple

user_admin_site = AdminSite(name="admin")
user_admin_site.register(get_user_model(), SemanticUserAdmin)
urlpatterns = [
    path(
        "admin/password_reset/",
        auth_views.PasswordResetView.as_view(form_class=SemanticPasswordResetForm),
        name="admin_password_reset",
    ),
    path("", user_admin_site.urls),
]


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
        self.assertIn('class="ui bulleted list"', content)
        self.assertIn('class="item"', content)
        self.assertIn('id="id_usable_password"', content)
        self.assertIn('name="set-password"', content)
        self.assertIn('name="unset-password"', content)
        self.assertGreaterEqual(content.count('class="four wide field"'), 2)
        self.assertRegex(content, r'<form class="ui form"')
        self.assertIn("novalidate", content)
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

    def test_default_password_change_form_is_replaced(self):
        self.admin_site.password_change_form = None

        register_semantic_password_change_form(self.admin_site)

        self.assertIs(
            self.admin_site.password_change_form,
            SemanticAdminSitePasswordChangeForm,
        )

    def test_custom_password_change_form_is_not_replaced(self):
        class CustomPasswordChangeForm(SemanticAdminSitePasswordChangeForm):
            pass

        self.admin_site.password_change_form = CustomPasswordChangeForm

        register_semantic_password_change_form(self.admin_site)

        self.assertIs(self.admin_site.password_change_form, CustomPasswordChangeForm)

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

    @override_settings(ROOT_URLCONF=__name__)
    def test_admin_password_reset_uses_login_style_card(self):
        response = self.client.get(reverse("admin_password_reset"))
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('id="password-reset"', content)
        self.assertIn('class="ui centered card"', content)
        self.assertIn('class="ui form"', content)
        self.assertIn('type="text"', content)
        self.assertIn('autocomplete="email"', content)
        self.assertIn('<label for="id_email" class="required">Email address:</label>', content)
        self.assertNotIn('type="email"', content)
        self.assertNotRegex(content, r"<(?:input|select|textarea)[^>]*\srequired(?:[=>\s]|$)")
        self.assertTrue(SemanticPasswordResetForm.base_fields["email"].required)
        self.assertNotIn('id="offscreen-menu"', content)
        self.assertNotIn('class="breadcrumbs"', content)
