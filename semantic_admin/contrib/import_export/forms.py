from django import forms
from import_export.forms import ExportForm, ImportForm
from semantic_forms import SemanticChoiceField

from semantic_admin.helpers import SemanticActionForm

from .widgets import SemanticExportActionSelect

try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _


def semantic_export_action_form_factory(formats: list) -> SemanticActionForm:
    """
    Returns an ActionForm subclass containing a ChoiceField populated with
    the given formats.
    """

    class _ExportActionForm(SemanticActionForm):
        """Action form with export format ChoiceField."""

        file_format = SemanticChoiceField(
            label=_("Format"),
            widget=SemanticExportActionSelect(),
            choices=formats,
            required=False,
        )

    _ExportActionForm.__name__ = "ExportActionForm"

    return _ExportActionForm


class SemanticImportForm(ImportForm):
    """Semantic import form."""

    input_format = SemanticChoiceField(label=_("Format"), choices=())

    @property
    def media(self) -> forms.Media:
        """Media."""
        media = self.fields["input_format"].widget.media
        return media + forms.Media(js=["import_export/guess_format.js"])


class SemanticExportForm(ExportForm):
    """Semantic export form."""

    file_format = SemanticChoiceField(label=_("Format"), choices=())
