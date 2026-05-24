from django.test import SimpleTestCase, override_settings
from django.utils.safestring import mark_safe

from semantic_admin.templatetags.semantic_app_list import get_semantic_app_list
from semantic_admin.templatetags.semantic_filters import (
    semantic_error_list,
    semantic_help_text,
)


def app_list():
    return [
        {
            "app_label": "library",
            "models": [
                {"object_name": "Author"},
                {"object_name": "Book"},
                {"object_name": "Shelf"},
            ],
        },
        {
            "app_label": "auth",
            "models": [{"object_name": "User"}],
        },
    ]


class SemanticAppListTests(SimpleTestCase):
    @override_settings(SEMANTIC_APP_LIST=None)
    def test_marks_current_app_active_without_semantic_app_list(self):
        apps = get_semantic_app_list(app_list(), "library")

        self.assertTrue(apps[0]["is_active"])
        self.assertFalse(apps[1]["is_active"])

    @override_settings(
        SEMANTIC_APP_LIST=[
            {
                "app_label": "library",
                "models": [{"object_name": "Author"}, {"object_name": "Book"}],
            },
        ]
    )
    def test_marks_filtered_semantic_app_active(self):
        apps = get_semantic_app_list(app_list(), "library")

        self.assertEqual([app["app_label"] for app in apps], ["library"])
        self.assertTrue(apps[0]["is_active"])
        self.assertEqual(
            [model["object_name"] for model in apps[0]["models"]],
            ["Author", "Book"],
        )

    @override_settings(
        SEMANTIC_APP_LIST=[
            {
                "app_label": "library",
                "models": [{"object_name": "Author"}],
            },
        ]
    )
    def test_filtered_semantic_app_defaults_first_active(self):
        apps = get_semantic_app_list(app_list(), "")

        self.assertTrue(apps[0]["is_active"])


class SemanticFormRenderTests(SimpleTestCase):
    def test_semantic_help_text_adds_semantic_list_classes(self):
        html = semantic_help_text(mark_safe("<ul><li>One</li><li>Two</li></ul>"))

        self.assertIn('<ul class="ui bulleted list">', html)
        self.assertEqual(html.count('<li class="item">'), 2)

    def test_semantic_error_list_uses_semantic_list_classes(self):
        html = semantic_error_list(["One", "Two"])

        self.assertIn('<ul class="ui bulleted list semantic-error-list">', html)
        self.assertEqual(html.count('<li class="item">'), 2)
