from django import forms
from django.contrib.admin.widgets import AutocompleteMixin


class SemanticAutocompleteMixin(AutocompleteMixin):
    """
    Select widget mixin that loads options from SemanticAutocompleteJsonView
    via AJAX. Renders the necessary data attributes for Semantic UI Dropdowns
    and adds the static form media.
    """

    template_name = "semantic_forms/forms/widgets/chooser.html"

    @property
    def media(self) -> None:
        """Media."""
        # Does not use django autocomplete media.


class SemanticAutocompleteSelect(  # type: ignore
    SemanticAutocompleteMixin, forms.Select
):
    """Semantic autocomplete select."""

    template_name = "semantic_forms/forms/widgets/select.html"


class SemanticAutocompleteSelectMultiple(  # type: ignore
    SemanticAutocompleteMixin, forms.SelectMultiple
):
    """Semantic autocomplete select multiple."""

    template_name = "semantic_forms/forms/widgets/select.html"
