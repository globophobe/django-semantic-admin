from django_filters import Filter, FilterSet
from django_filters.filters import (
    AllValuesMultipleFilter,
    ChoiceFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
    TypedMultipleChoiceFilter,
)


class ExcludeAllFilterSet(FilterSet):
    """
    Somewhat debatable to have this in core.
    However, reversing logic with exclude parameter is a useful feature. 
    https://django-filter.readthedocs.io/en/master/guide/tips.html
    """

    def __init__(self, *args, **kwargs):
        self.exclude = kwargs.pop("exclude", False)
        super().__init__(*args, **kwargs)
        if self.exclude:
            for f in self.filters:
                self.filters[f].exclude = self.exclude


class FilterOrExcludeMixin(Filter):
    def get_method(self, qs):
        """Return filter method based on whether we're excluding
           or simply filtering.
        """
        return qs.exclude if self.exclude else qs.filter


class SemanticChoiceFilter(FilterOrExcludeMixin, ChoiceFilter):
    pass


class SemanticMultipleChoiceFilter(FilterOrExcludeMixin, MultipleChoiceFilter):
    pass


class SemanticTypedMultipleChoiceFilter(
    FilterOrExcludeMixin, TypedMultipleChoiceFilter
):
    pass


class SemanticMultipleAllValuesFilter(FilterOrExcludeMixin, AllValuesMultipleFilter):
    pass


class SemanticModelMultipleChoiceFilter(
    FilterOrExcludeMixin, ModelMultipleChoiceFilter
):
    pass
