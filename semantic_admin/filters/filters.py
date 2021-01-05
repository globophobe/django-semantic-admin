from django_filters.filters import (
    AllValuesMultipleFilter,
    ChoiceFilter,
    DateFilter,
    DateTimeFilter,
    Filter,
    ModelChoiceFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
    TimeFilter,
    TypedMultipleChoiceFilter,
)
from semantic_admin.fields import (
    SemanticChoiceField,
    SemanticDateField,
    SemanticDateTimeField,
    SemanticModelChoiceField,
    SemanticModelMultipleChoiceField,
    SemanticMultipleChoiceField,
    SemanticTimeField,
    SemanticTypedChoiceField,
    SemanticTypedMultipleChoiceField,
)


class FilterOrExcludeMixin(Filter):
    def get_method(self, qs):
        """Return filter method based on whether we're excluding or simply filtering"""
        return qs.exclude if self.exclude else qs.filter


class SemanticDateTimeFilter(FilterOrExcludeMixin, DateTimeFilter):
    field_class = SemanticDateTimeField


class SemanticDateFilter(FilterOrExcludeMixin, DateFilter):
    field_class = SemanticDateField


class SemanticTimeFilter(FilterOrExcludeMixin, TimeFilter):
    field_class = SemanticTimeField


class SemanticChoiceFilter(FilterOrExcludeMixin, ChoiceFilter):
    field_class = SemanticChoiceField


class SemanticMultipleChoiceFilter(FilterOrExcludeMixin, MultipleChoiceFilter):
    field_class = SemanticMultipleChoiceField


class SemanticTypedChoiceFilter(FilterOrExcludeMixin, TypedMultipleChoiceFilter):
    field_class = SemanticTypedChoiceField


class SemanticTypedMultipleChoiceFilter(
    FilterOrExcludeMixin, TypedMultipleChoiceFilter
):
    field_class = SemanticTypedMultipleChoiceField


class SemanticMultipleAllValuesFilter(FilterOrExcludeMixin, AllValuesMultipleFilter):
    field_class = SemanticChoiceField


class SemanticModelChoiceFilter(FilterOrExcludeMixin, ModelChoiceFilter):
    field_class = SemanticModelChoiceField


class SemanticModelMultipleChoiceFilter(
    FilterOrExcludeMixin, ModelMultipleChoiceFilter
):
    field_class = SemanticModelMultipleChoiceField
