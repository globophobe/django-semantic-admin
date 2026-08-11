from django.contrib.admin.helpers import ActionForm
from django.utils.translation import gettext_lazy as _
from semantic_forms.fields import SemanticChoiceField


class SemanticActionForm(ActionForm):
    """Semantic action form."""

    action = SemanticChoiceField(label=_("Action:"))
