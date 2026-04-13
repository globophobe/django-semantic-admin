from django.apps import AppConfig


class SemanticAdminTestsAppConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "semantic_admin.tests.app"
    label = "semantic_admin_tests"
    verbose_name = "semantic_admin tests"

