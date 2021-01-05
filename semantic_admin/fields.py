from django import forms

from .widgets import (
    SemanticDateInput,
    SemanticDateTimeInput,
    SemanticSelect,
    SemanticSelectMultiple,
    SemanticTimeInput,
)


class SemanticDateTimeField(forms.DateTimeField):
    widget = SemanticDateTimeInput


class SemanticDateField(forms.DateField):
    widget = SemanticDateInput


class SemanticTimeField(forms.TimeField):
    widget = SemanticTimeInput


# Single choice
class SemanticChoiceField(forms.ChoiceField):
    widget = SemanticSelect


class SemanticTypedChoiceField(forms.TypedChoiceField):
    widget = SemanticSelect


class SemanticModelChoiceField(forms.ModelChoiceField):
    widget = SemanticSelect


# Multiple choice
class SemanticMultipleChoiceField(forms.MultipleChoiceField):
    widget = SemanticSelectMultiple


class SemanticTypedMultipleChoiceField(forms.TypedMultipleChoiceField):
    widget = SemanticSelectMultiple


class SemanticModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    widget = SemanticSelectMultiple
