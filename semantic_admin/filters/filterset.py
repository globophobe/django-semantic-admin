from copy import deepcopy

from django.db import models
from django.db.models.fields.related import ManyToManyRel, ManyToOneRel, OneToOneRel
from django_filters import FilterSet
from django_filters.filters import BaseInFilter, BaseRangeFilter
from django_filters.filterset import FILTER_FOR_DBFIELD_DEFAULTS
from django_filters.utils import try_dbfield

from .filters import (
    SemanticChoiceFilter,
    SemanticModelChoiceFilter,
    SemanticModelMultipleChoiceFilter,
)

SEMANTIC_FILTER_FOR_DBFIELD_DEFAULTS = {
    # Forward relationships
    models.OneToOneField: SemanticModelChoiceFilter,
    models.ForeignKey: SemanticModelChoiceFilter,
    models.ManyToManyField: SemanticModelMultipleChoiceFilter,
    # Reverse relationships
    OneToOneRel: SemanticModelChoiceFilter,
    ManyToOneRel: SemanticModelMultipleChoiceFilter,
    ManyToManyRel: SemanticModelMultipleChoiceFilter,
}


class SemanticFilterSet(FilterSet):
    FILTER_DEFAULTS = deepcopy(FILTER_FOR_DBFIELD_DEFAULTS)

    for field, filter_class in SEMANTIC_FILTER_FOR_DBFIELD_DEFAULTS.items():
        FILTER_DEFAULTS[field]["filter_class"] = filter_class

    def __init__(self, *args, **kwargs):
        self.passed_validation = kwargs.pop("passed_validation", False)
        super().__init__(*args, **kwargs)

    @classmethod
    def filter_for_lookup(cls, field, lookup_type):
        DEFAULTS = dict(cls.FILTER_DEFAULTS)
        if hasattr(cls, "_meta"):
            DEFAULTS.update(cls._meta.filter_overrides)

        data = try_dbfield(DEFAULTS.get, field.__class__) or {}
        filter_class = data.get("filter_class")
        params = data.get("extra", lambda field: {})(field)

        # if there is no filter class, exit early
        if not filter_class:
            return None, {}

        # perform lookup specific checks
        if lookup_type == "exact" and getattr(field, "choices", None):

            # BEGIN CUSTOMIZATION
            return SemanticChoiceFilter, {"choices": field.choices}
            # END CUSTOMIZATION

        if lookup_type == "isnull":
            data = try_dbfield(DEFAULTS.get, models.BooleanField)

            filter_class = data.get("filter_class")
            params = data.get("extra", lambda field: {})(field)
            return filter_class, params

        if lookup_type == "in":

            class ConcreteInFilter(BaseInFilter, filter_class):
                pass

            ConcreteInFilter.__name__ = cls._csv_filter_class_name(
                filter_class, lookup_type
            )

            return ConcreteInFilter, params

        if lookup_type == "range":

            class ConcreteRangeFilter(BaseRangeFilter, filter_class):
                pass

            ConcreteRangeFilter.__name__ = cls._csv_filter_class_name(
                filter_class, lookup_type
            )

            return ConcreteRangeFilter, params

        return filter_class, params


class SemanticExcludeAllFilterSet(SemanticFilterSet):
    """
    Debatable to have this
    https://django-filter.readthedocs.io/en/master/guide/tips.html
    """

    def __init__(self, *args, **kwargs):
        self.exclude = kwargs.pop("exclude", False)
        super().__init__(*args, **kwargs)
        if self.exclude:
            for f in self.filters:
                exclude = self.filters[f].exclude
                self.filters[f].exclude = not exclude
