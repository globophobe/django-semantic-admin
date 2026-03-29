from typing import Iterable

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from semantic_forms.filters import SemanticFilterSet, SemanticModelMultipleChoiceFilter

from .models import Person, Picture


class PersonFilter(SemanticFilterSet):
    """Person filter."""

    favorite_pictures = SemanticModelMultipleChoiceFilter(
        label=_("favorite pictures"),
        queryset=Picture.objects.exclude(favorites=None),
        method="filter_favorite_pictures",
    )

    def filter_favorite_pictures(
        self, queryset: QuerySet, name: str, value: Iterable[int]
    ) -> QuerySet:
        """Filter by favorite pictures."""
        if not value:
            return queryset
        else:
            queryset = queryset.filter(favorites__picture__in=value)
            return queryset.distinct()

    class Meta:
        model = Person
        fields = ("friends", "favorite_pictures")
