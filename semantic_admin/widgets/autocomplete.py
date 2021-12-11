from django import forms
from django.contrib.admin.widgets import AutocompleteMixin


class SemanticAutocompleteMixin(AutocompleteMixin):
    """
    Select widget mixin that loads options from SemanticAutocompleteJsonView
    via AJAX. Renders the necessary data attributes for Semantic UI Dropdowns
    and adds the static form media.
    """

    template_name = "semantic_ui/forms/widgets/chooser.html"

    @property
    def media(self):
        # No media.
        pass


class SemanticAutocompleteSelect(  # type: ignore
    SemanticAutocompleteMixin, forms.Select
):
    template_name = "semantic_ui/forms/widgets/select.html"


class SemanticAutocompleteSelectMultiple(  # type: ignore
    SemanticAutocompleteMixin, forms.SelectMultiple
):
    template_name = "semantic_ui/forms/widgets/select.html"
