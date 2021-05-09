from django import forms


class SemanticChangelistCheckboxInput(forms.CheckboxInput):
    template_name = "semantic_ui/forms/widgets/changelist_checkbox.html"


class SemanticActionCheckboxInput(forms.CheckboxInput):
    template_name = "semantic_ui/forms/widgets/action_checkbox.html"
