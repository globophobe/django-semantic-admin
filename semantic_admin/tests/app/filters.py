from semantic_forms.filters import SemanticFilterSet, SemanticModelChoiceFilter

from .models import Category, Event


class EventFilter(SemanticFilterSet):
    category = SemanticModelChoiceFilter(queryset=Category.objects.all())

    class Meta:
        model = Event
        fields = ("category",)

