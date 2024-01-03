from typing import Any, Optional

from django import forms


class SemanticSelect(forms.Select):
    """Semantic select."""

    template_name = "semantic_ui/forms/widgets/select.html"


class SemanticSelectMultiple(forms.SelectMultiple, SemanticSelect):
    """Semantic select multiple."""


class SemanticCheckboxInput(forms.CheckboxInput):
    """Semantic checkbox input."""

    template_name = "semantic_ui/forms/widgets/checkbox.html"


class SemanticCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    """Semantic checkbox select multiple."""

    template_name = "semantic_ui/forms/widgets/checkbox_select.html"
    option_template_name = "semantic_ui/forms/widgets/checkbox_option.html"


class SemanticDateTimeInput(forms.DateTimeInput):
    """Semantic date time input."""

    template_name = "semantic_ui/forms/widgets/datetime.html"


class SemanticDateInput(forms.DateInput):
    """Semantic date input."""

    template_name = "semantic_ui/forms/widgets/date.html"


class SemanticTimeInput(forms.TimeInput):
    """Semantic time input."""

    template_name = "semantic_ui/forms/widgets/time.html"


class SemanticEmailInput(forms.EmailInput):
    """Semantic email input."""
    # TODO
    # template_name = "semantic_ui/forms/widgets/email.html"


class SemanticFileInput(forms.ClearableFileInput):
    """Semantic file input."""

    template_name = "semantic_ui/forms/widgets/clearable_file_input.html"


class SemanticImageInput(SemanticFileInput):
    """Semantic image input."""


class SemanticClearableFileInput(forms.ClearableFileInput):
    """Semantic clearable file input."""

    template_name = "semantic_ui/forms/widgets/clearable_file_input.html"


class SemanticNumberInput(forms.NumberInput):
    """Semantic number input."""


class SemanticPasswordInput(forms.NumberInput):
    """Semantic password input."""


class SemanticRadioSelect(forms.RadioSelect):
    """Semantic radio select."""

    template_name = "semantic_ui/forms/widgets/radio.html"
    option_template_name = "semantic_ui/forms/widgets/radio_option.html"


class SemanticTextarea(forms.Textarea):
    """Semantic textara."""

    template_name = "semantic_ui/forms/widgets/textarea.html"


class SemanticTextInput(forms.Textarea):
    """Semantic text input."""

    template_name = "semantic_ui/forms/widgets/text.html"


class SemanticURLInput(forms.URLInput):
    """Semantic URL input."""


class RangeWidget(forms.MultiWidget):
    """Range widget."""

    def decompress(self, value: Any) -> list:
        """Decompress."""
        if value:
            return [value.start, value.stop]
        return [None, None]


class SemanticDateRangeWidget(RangeWidget):
    """Semantic date range widget."""

    def __init__(self, attrs: Optional[dict] = None) -> None:
        """Initialize."""
        widgets = [SemanticDateInput, SemanticDateInput]
        super().__init__(widgets, attrs)


class SemanticTimeRangeWidget(RangeWidget):
    """Semantic time range widget."""

    def __init__(self, attrs: Optional[dict] =None) -> None:
        """Initialize."""
        widgets = [SemanticTimeInput(), SemanticTimeInput()]
        super().__init__(widgets, attrs)
