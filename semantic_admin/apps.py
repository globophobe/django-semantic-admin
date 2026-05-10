from django.apps import AppConfig


class SemanticAdminConfig(AppConfig):
    default = True
    default_auto_field = "django.db.models.AutoField"
    name = "semantic_admin"
    verbose_name = "Semantic admin"

    def ready(self) -> None:
        from semantic_admin.auth.admin import init_semantic_auth_admin

        init_semantic_auth_admin()
