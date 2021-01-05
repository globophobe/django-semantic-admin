from django.contrib.admin.helpers import ActionForm
from django.utils.translation import ugettext_lazy as _

from .fields import SemanticChoiceField


class SemanticActionForm(ActionForm):
    action = SemanticChoiceField(label=_("Action:"))
