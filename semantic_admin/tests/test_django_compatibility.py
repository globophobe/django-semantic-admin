from copy import deepcopy
from html.parser import HTMLParser
from unittest import skipUnless

import django
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import path, reverse
from django.utils import timezone

from semantic_admin import SemanticModelAdmin
from semantic_admin.auth.admin import SemanticUserAdmin
from semantic_admin.tests.app.models import Category, Event


class RestrictedCategoryAdmin(SemanticModelAdmin):
    list_display = ("id", "name")
    list_editable = ("name",)
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj) and (
            obj is None or obj.name != "Protected"
        )


class ActionCategoryAdmin(SemanticModelAdmin):
    actions = ("approve",)

    def approve(self, request, queryset):
        queryset.update(name="Approved")

    if django.VERSION >= (6, 1):
        approve = admin.action(
            description="Approve category", location=admin.ActionLocation.CHANGE_FORM
        )(approve)


bulk_site = admin.AdminSite(name="bulk_admin")
bulk_site.register(Category, RestrictedCategoryAdmin)
action_site = admin.AdminSite(name="action_admin")
action_site.register(Category, ActionCategoryAdmin)
csp_site = admin.AdminSite(name="csp_admin")
csp_site.register(Category, SemanticModelAdmin)
csp_site.register(Event, SemanticModelAdmin)
csp_site.register(get_user_model(), SemanticUserAdmin)
urlpatterns = [
    path("csp/", csp_site.urls),
    path("bulk/", bulk_site.urls),
    path("actions/", action_site.urls),
]


@override_settings(ROOT_URLCONF=__name__)
class ChangelistPermissionTests(TestCase):
    def setUp(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                "reviewer", is_staff=True, is_superuser=True
            )
        )
        self.protected = Category.objects.create(name="Protected")
        self.editable = Category.objects.create(name="Editable")
        self.url = reverse("bulk_admin:semantic_admin_tests_category_changelist")

    def test_object_permissions_apply_to_rendered_fields_and_saved_rows(self):
        response = self.client.get(self.url)
        forms = {
            form.instance.pk: form for form in response.context["cl"].formset.forms
        }
        self.assertEqual(set(forms[self.protected.pk].fields), {"id"})
        self.assertEqual(set(forms[self.editable.pk].fields), {"id", "name"})

        response = self.client.post(
            self.url,
            {
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "2",
                "form-0-id": str(self.protected.pk),
                "form-0-name": "Unauthorized change",
                "form-1-id": str(self.editable.pk),
                "form-1-name": "Permitted change",
                "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            list(Category.objects.order_by("pk").values_list("name", flat=True)),
            ["Protected", "Permitted change"],
        )

    def test_new_row_in_bulk_edit_is_rejected_and_other_writes_are_rolled_back(self):
        response = self.client.post(
            self.url,
            {
                "form-TOTAL_FORMS": "2",
                "form-INITIAL_FORMS": "1",
                "form-0-id": str(self.editable.pk),
                "form-0-name": "Must roll back",
                "form-1-id": "",
                "form-1-name": "Unauthorized new category",
                "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            list(Category.objects.order_by("pk").values_list("name", flat=True)),
            ["Protected", "Editable"],
        )


@skipUnless(django.VERSION >= (6, 1), "Change-form actions require Django 6.1")
@override_settings(ROOT_URLCONF=__name__)
class ChangeFormActionTests(TestCase):
    def test_action_is_rendered_and_applies_only_to_the_current_object(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                "reviewer", is_staff=True, is_superuser=True
            )
        )
        selected = Category.objects.create(name="Review me")
        other = Category.objects.create(name="Other")
        url = reverse(
            "action_admin:semantic_admin_tests_category_change", args=[selected.pk]
        )
        response = self.client.get(url)
        field_name = response.context["action_form"]["action"].html_name
        self.assertContains(response, f'name="{field_name}"')
        self.assertContains(response, 'value="approve"')
        self.assertContains(response, f'name="{ACTION_CHECKBOX_NAME}"')

        response = self.client.post(
            url,
            {
                field_name: "approve",
                ACTION_CHECKBOX_NAME: str(selected.pk),
                "index": "0",
            },
        )
        self.assertEqual(response.status_code, 302)
        selected.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(selected.name, "Approved")
        self.assertEqual(other.name, "Other")


class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"} or (
            tag == "link" and dict(attrs).get("rel") == "stylesheet"
        ):
            self.assets.append((tag, dict(attrs)))


@skipUnless(django.VERSION >= (6, 1), "Native nonce rendering requires Django 6.1")
@override_settings(ROOT_URLCONF=__name__)
class CspRenderingTests(TestCase):
    def test_rendered_admin_assets_use_the_response_policy_nonce(self):
        from django.utils.csp import CSP

        templates = deepcopy(settings.TEMPLATES)
        templates[0]["OPTIONS"]["context_processors"].append(
            "django.template.context_processors.csp"
        )
        middleware = [
            *settings.MIDDLEWARE,
            "django.middleware.csp.ContentSecurityPolicyMiddleware",
        ]
        category = Category.objects.create(name="Category")
        event = Event.objects.create(
            category=category, name="Event", when=timezone.now()
        )
        user = get_user_model().objects.create_user(
            "reviewer", is_staff=True, is_superuser=True
        )
        with override_settings(
            TEMPLATES=templates,
            MIDDLEWARE=middleware,
            SECURE_CSP={"script-src": [CSP.NONCE]},
        ):
            self._assert_nonce(reverse("csp_admin:login"))
            self.client.force_login(user)
            urls = [
                reverse("csp_admin:index"),
                reverse("csp_admin:semantic_admin_tests_event_changelist"),
                reverse("csp_admin:semantic_admin_tests_event_change", args=[event.pk]),
                reverse("csp_admin:semantic_admin_tests_event_delete", args=[event.pk]),
                reverse("csp_admin:auth_user_add"),
                reverse("csp_admin:auth_user_password_change", args=[user.pk]),
                reverse("csp_admin:password_change"),
            ]
            for url in urls:
                with self.subTest(url=url):
                    self._assert_nonce(url)

    def _assert_nonce(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        policy = response.headers["Content-Security-Policy"]
        nonce = policy.split("'nonce-", 1)[1].split("'", 1)[0]
        parser = AssetParser()
        parser.feed(response.content.decode())
        self.assertGreater(len(parser.assets), 0)
        for tag, attrs in parser.assets:
            with self.subTest(tag=tag, src=attrs.get("src"), href=attrs.get("href")):
                self.assertEqual(attrs.get("nonce"), nonce)
