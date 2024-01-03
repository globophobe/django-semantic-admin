from django import forms
from import_export.admin import ExportActionMixin, ExportMixin, ImportMixin

from semantic_admin import SemanticModelAdmin

from .forms import (
    SemanticExportForm,
    SemanticImportForm,
    semantic_export_action_form_factory,
)


class SemanticImportMixin(ImportMixin):
    """Semantic import mixin."""

    import_form_class = SemanticImportForm


class SemanticExportMixin(ExportMixin):
    """Semantic export mixin."""

    export_form_class = SemanticExportForm


class SemanticExportActionMixin(ExportActionMixin):
    """Semantic export action mixin."""

    export_form_class = SemanticExportForm

    def __init__(self, *args, **kwargs) -> None:
        """
        Adds a custom action form initialized with the available export
        formats.
        """
        super().__init__(*args, **kwargs)
        choices = []
        formats = self.get_export_formats()
        if formats:
            for i, f in enumerate(formats):
                choices.append((str(i), f().get_title()))

        if len(formats) > 1:
            choices.insert(0, ("", "---"))
        # region CUSTOM
        self.action_form = semantic_export_action_form_factory(choices)
        # endregion

    @property
    def media(self) -> forms.Media:
        """Form media."""
        return super().media


class SemanticExportActionMixin(SemanticExportActionMixin):
    """Semantic export action mixin."""


class SemanticImportExportMixin(SemanticExportMixin, SemanticImportMixin):
    """Semantic import export mixin."""

    #: template for change_list view
    import_export_change_list_template = (
        "admin/import_export/change_list_import_export.html"
    )


class SemanticExportActionMixin(SemanticExportActionMixin, SemanticModelAdmin):
    """Semantic export action mixin."""


class SemanticImportExportModelAdmin(SemanticImportExportMixin, SemanticModelAdmin):
    """Semantic import export model admin."""


class SemanticExportActionModelAdmin(SemanticExportActionMixin, SemanticModelAdmin):
    """Semantic export action model admin."""


class SemanticImportExportActionModelAdmin(
    SemanticImportMixin, SemanticExportActionModelAdmin
):
    """Semantic import export action model admin."""
