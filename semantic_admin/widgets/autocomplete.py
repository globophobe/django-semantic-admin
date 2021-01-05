from django import forms
from django.contrib.admin.widgets import AutocompleteMixin


class SemanticAutocompleteMixin(AutocompleteMixin):
    """
    Select widget mixin that loads options from SemanticAutocompleteJsonView
    via AJAX. Renders the necessary data attributes for Semantic UI Dropdowns
    and adds the static form media.
    """

    template_name = "semantic_ui/forms/widgets/chooser.html"

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault("class", "")
        attrs.update(
            {
                "data-ajax-url": self.get_url(),
                "class": attrs["class"] + (" " if attrs["class"] else ""),
            }
        )
        return attrs

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
