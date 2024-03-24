from django.contrib.admin.helpers import ActionForm
from semantic_forms.fields import SemanticChoiceField

try:
    from django.utils.translation import gettext_lazy as _  # Django >= 4
except ImportError:
    from django.utils.translation import ugettext_lazy as _


class SemanticActionForm(ActionForm):
    """Semantic action form."""

    action = SemanticChoiceField(label=_("Action:"))
