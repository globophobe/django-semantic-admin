from django.contrib.admin.helpers import ActionForm

from .fields import SemanticChoiceField

try:
    from django.utils.translation import gettext_lazy as _  # Django >= 4
except ImportError:
    from django.utils.translation import ugettext_lazy as _


class SemanticActionForm(ActionForm):
    action = SemanticChoiceField(label=_("Action:"))
