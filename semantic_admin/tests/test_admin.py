from django.contrib import admin as django_admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from semantic_admin import SemanticStackedInline, SemanticTabularInline
from semantic_admin.auth.forms import SemanticAdminSitePasswordChangeForm
from semantic_admin.tests.app.models import Category, Event, EventNote
from semantic_admin.utils import get_javascript_catalog_url
from semantic_admin.widgets import SemanticChangelistCheckboxInput
from semantic_forms.widgets import SemanticCheckboxInput, SemanticDateTimeInput


class EventNoteInline(SemanticTabularInline):
    model = EventNote
    fields = ("label",)
    extra = 0


class EventNoteStackedInline(SemanticStackedInline):
    model = EventNote
    fields = ("label",)
    extra = 0


class AdminMediaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )
        cls.category = Category.objects.create(name="Conference")
        cls.event = Event.objects.create(
            category=cls.category,
            name="Launch Day",
            when=timezone.now(),
            is_active=True,
        )
        EventNote.objects.create(event=cls.event, label="Checklist")

    def setUp(self):
        super().setUp()
        self.admin_site = AdminSite()
        self.request_factory = RequestFactory()
        self.client.force_login(self.user)

    def assert_admin_jquery_bootstrap_once(self, response):
        content = response.content.decode()

        jquery_count = content.count("admin/js/vendor/jquery/jquery.js")
        jquery_count += content.count("admin/js/vendor/jquery/jquery.min.js")

        self.assertEqual(jquery_count, 1)
        self.assertEqual(content.count("admin/js/jquery.init.js"), 1)
        self.assertNotIn("ajax.googleapis.com/ajax/libs/jquery", content)

    def assert_javascript_catalog_once(self, response):
        content = response.content.decode()
        catalog_url = get_javascript_catalog_url()

        self.assertIsNotNone(catalog_url)
        self.assertEqual(content.count(f'src="{catalog_url}"'), 1)

    def test_login_form_uses_semantic_admin_auth_form_validation(self):
        self.client.logout()

        response = self.client.get(reverse("admin:login"))
        content = response.content.decode()

        self.assertRegex(content, r'<form class="ui form"[^>]*>')
        self.assertNotIn("novalidate", content)
        self.assertNotRegex(content, r"<(?:input|select|textarea)[^>]*\srequired(?:[=>\s]|$)")

    def test_login_field_errors_use_semantic_markup(self):
        self.client.logout()

        response = self.client.post(
            reverse("admin:login"),
            {"username": "", "password": ""},
        )
        content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("ui error message", content)
        self.assertIn("field error", content)
        self.assertIn('<ul class="ui bulleted list semantic-error-list">', content)
        self.assertIn('<li class="item">This field is required.</li>', content)
        self.assertNotIn("errorlist", content)

    def test_inline_delete_field_includes_semantic_checkbox_media(self):
        request = self.request_factory.get("/")
        request.user = self.user

        inline = EventNoteInline(Event, self.admin_site)
        formset_class = inline.get_formset(request, self.event)
        formset = formset_class(instance=self.event)

        self.assertIn("semantic_forms/semanticCheckbox.js", formset.media._js)

    def test_stacked_inline_delete_field_includes_semantic_checkbox_media(self):
        request = self.request_factory.get("/")
        request.user = self.user

        inline = EventNoteStackedInline(Event, self.admin_site)
        formset_class = inline.get_formset(request, self.event)
        formset = formset_class(instance=self.event)

        self.assertIn("semantic_forms/semanticCheckbox.js", formset.media._js)

    def test_change_form_uses_django_admin_jquery_once(self):
        response = self.client.get(
            reverse("admin:semantic_admin_tests_event_change", args=(self.event.pk,))
        )

        self.assert_admin_jquery_bootstrap_once(response)
        self.assert_javascript_catalog_once(response)

    def test_password_change_uses_semantic_breadcrumbs(self):
        request = self.request_factory.get("/")
        request.user = self.user

        content = render_to_string(
            "registration/password_change_form.html",
            request=request,
        )

        self.assertIn('class="ui large breadcrumb"', content)
        self.assertIn('class="right chevron icon divider"', content)
        self.assertIn("novalidate", content)
        self.assertNotIn('class="breadcrumbs"', content)

    def test_password_change_form_disables_native_required_attrs(self):
        request = self.request_factory.get("/")
        request.user = self.user
        form = SemanticAdminSitePasswordChangeForm(user=self.user)

        content = render_to_string(
            "registration/password_change_form.html",
            {"form": form},
            request=request,
        )

        self.assertIn("novalidate", content)
        self.assertNotRegex(
            content,
            r"<(?:input|select|textarea)[^>]*\srequired(?:[=>\s]|$)",
        )

    def test_password_change_errors_use_semantic_message(self):
        request = self.request_factory.get("/")
        request.user = self.user
        form = PasswordChangeForm(
            user=self.user,
            data={
                "old_password": "wrong",
                "new_password1": "new-password-123",
                "new_password2": "different-password-123",
            },
        )
        self.assertFalse(form.is_valid())

        content = render_to_string(
            "registration/password_change_form.html",
            {"form": form},
            request=request,
        )

        self.assertIn('class="ui error message"', content)
        self.assertIn("novalidate", content)
        self.assertIn('class="field field-old-password error"', content)
        self.assertIn('class="field field-new-password2 error"', content)
        self.assertIn('class="ui bulleted list semantic-error-list"', content)
        self.assertNotIn('class="errornote"', content)

    def test_logged_out_uses_login_style_card(self):
        request = self.request_factory.get("/")
        request.user = self.user

        content = render_to_string(
            "registration/logged_out.html",
            {"title": "Logged out"},
            request=request,
        )

        self.assertIn('id="logged-out"', content)
        self.assertIn('class="ui centered card"', content)
        self.assertIn("Log in again", content)
        self.assertIn('class="password-reset-link"', content)

    def test_change_form_keeps_non_addable_inline_with_existing_rows(self):
        response = self.client.get(
            reverse("admin:semantic_admin_tests_event_change", args=(self.event.pk,))
        )

        self.assertContains(response, 'id="notes-group"')

    def test_add_view_hides_empty_non_addable_inline_group(self):
        response = self.client.get(reverse("admin:semantic_admin_tests_event_add"))

        self.assertNotContains(response, 'id="notes-group"')

    def test_delete_confirmation_uses_django_admin_jquery_once(self):
        response = self.client.get(
            reverse("admin:semantic_admin_tests_event_delete", args=(self.event.pk,))
        )

        self.assert_admin_jquery_bootstrap_once(response)

    def test_change_list_uses_django_admin_jquery_once(self):
        response = self.client.get(reverse("admin:semantic_admin_tests_event_changelist"))

        self.assert_admin_jquery_bootstrap_once(response)
        self.assert_javascript_catalog_once(response)

    def test_changelist_actions_keep_equal_width_select_group(self):
        response = self.client.get(reverse("admin:semantic_admin_tests_event_changelist"))
        content = response.content.decode()

        self.assertIn('class="actions inline equal width fields"', content)
        self.assertIn('class="field action-select-field"', content)
        self.assertIn('style="margin: 0 !important;', content)
        self.assertIn('padding: 0"', content)
        self.assertIn('class="action-label"', content)

    def test_header_object_tools_use_fixed_slots(self):
        response = self.client.get(reverse("admin:semantic_admin_tests_event_changelist"))
        content = response.content.decode()

        self.assertIn("semantic-admin-content-header", content)
        self.assertIn("eight wide field semantic-admin-title-field", content)
        self.assertEqual(content.count("four wide field noprint semantic-admin-object-tool-field"), 2)
        self.assertIn("addlink", content)
        self.assertNotIn("six wide field noprint", content)
        self.assertNotIn("semantic-admin-object-tool-spacer", content)

        response = self.client.get(
            reverse("admin:semantic_admin_tests_event_change", args=(self.event.pk,))
        )
        content = response.content.decode()

        self.assertEqual(content.count("four wide field noprint semantic-admin-object-tool-field"), 2)
        self.assertIn("historylink", content)
        self.assertNotIn('<div class="four wide field" style="margin-bottom: 0;"></div>', content)

    def test_change_list_keeps_filterset_media_in_combined_media(self):
        response = self.client.get(reverse("admin:semantic_admin_tests_event_changelist"))

        self.assertContains(response, "semantic_forms/semanticDropdown.js")

    def test_change_form_uses_semantic_widgets_for_model_fields(self):
        request = self.request_factory.get("/")
        request.user = self.user
        model_admin = django_admin.site._registry[Event]

        form_class = model_admin.get_form(request, self.event)

        self.assertIsInstance(form_class.base_fields["when"].widget, SemanticDateTimeInput)
        self.assertIsInstance(
            form_class.base_fields["is_active"].widget,
            SemanticCheckboxInput,
        )

    def test_changelist_formset_uses_semantic_checkbox_widget_for_boolean_field(self):
        request = self.request_factory.get("/")
        request.user = self.user
        model_admin = django_admin.site._registry[Event]

        formset_class = model_admin.get_changelist_formset(request)

        self.assertIsInstance(
            formset_class.form.base_fields["is_active"].widget,
            SemanticChangelistCheckboxInput,
        )
