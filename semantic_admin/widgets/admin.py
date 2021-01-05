from django import forms


class SemanticActionCheckboxInput(forms.CheckboxInput):
    template_name = "semantic_ui/forms/widgets/changelist_checkbox.html"
