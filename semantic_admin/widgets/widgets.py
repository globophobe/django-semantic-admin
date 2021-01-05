from django import forms


class SemanticSelect(forms.Select):
    template_name = "semantic_ui/forms/widgets/select.html"


class SemanticSelectMultiple(forms.SelectMultiple, SemanticSelect):
    pass


class SemanticCheckboxInput(forms.CheckboxInput):
    template_name = "semantic_ui/forms/widgets/checkbox.html"


class SemanticCheckboxSelectMultiple(forms.CheckboxSelectMultiple):
    template_name = "semantic_ui/forms/widgets/checkbox_select.html"
    option_template_name = "semantic_ui/forms/widgets/checkbox_option.html"


class SemanticDateTimeInput(forms.DateTimeInput):
    template_name = "semantic_ui/forms/widgets/datetime.html"


class SemanticDateInput(forms.DateInput):
    template_name = "semantic_ui/forms/widgets/date.html"


class SemanticTimeInput(forms.TimeInput):
    template_name = "semantic_ui/forms/widgets/time.html"


class SemanticEmailInput(forms.EmailInput):
    # TODO
    # template_name = "semantic_ui/forms/widgets/email.html"
    pass


class SemanticFileInput(forms.ClearableFileInput):
    template_name = "semantic_ui/forms/widgets/clearable_file_input.html"


class SemanticImageInput(SemanticFileInput):
    pass


class SemanticClearableFileInput(forms.ClearableFileInput):
    template_name = "semantic_ui/forms/widgets/clearable_file_input.html"


class SemanticNumberInput(forms.NumberInput):
    pass


class SemanticPasswordInput(forms.NumberInput):
    pass


class SemanticRadioSelect(forms.RadioSelect):
    template_name = "semantic_ui/forms/widgets/radio.html"
    option_template_name = "semantic_ui/forms/widgets/radio_option.html"


class SemanticTextarea(forms.Textarea):
    template_name = "semantic_ui/forms/widgets/textarea.html"


class SemanticTextInput(forms.Textarea):
    template_name = "semantic_ui/forms/widgets/text.html"


class SemanticURLInput(forms.URLInput):
    pass


class RangeWidget(forms.MultiWidget):
    def decompress(self, value):
        if value:
            return [value.start, value.stop]
        return [None, None]


class SemanticDateRangeWidget(RangeWidget):
    def __init__(self, attrs=None):
        widgets = [SemanticDateInput, SemanticDateInput]
        super().__init__(widgets, attrs)


class SemanticTimeRangeWidget(RangeWidget):
    def __init__(self, attrs=None):
        widgets = [SemanticTimeInput(), SemanticTimeInput()]
        super().__init__(widgets, attrs)
