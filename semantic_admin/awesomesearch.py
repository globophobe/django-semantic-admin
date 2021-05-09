import operator
from functools import reduce

from django.contrib import admin
from django.contrib.admin.utils import lookup_needs_distinct
from django.contrib.admin.views.main import ChangeList
from django.db import models
from django.forms import ModelMultipleChoiceField
from django.forms.fields import MultipleChoiceField
from django.utils.http import urlencode


class AwesomeSearchChangeList(ChangeList):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            request = args[0]
        except IndexError:
            pass
        else:
            # WTF? Wasn't this already set.
            self.full_result_count = self.model_admin.get_queryset(request).count()

    def get_query_string(self, new_params=None, remove=None):
        params = super().get_query_string(new_params=new_params, remove=remove)
        filterset_params = self.get_filterset_params()
        if filterset_params:
            if len(params) > 1:
                params += "&"
            params += filterset_params
        return params

    def get_filterset_params(self):
        filterset_params = getattr(self.model_admin, "filterset_params", None)
        exclude = getattr(self.model_admin, "filterset_exclude", None)
        params = ""
        if filterset_params:
            if exclude:
                filterset_params["_exclude"] = "true"
            for key in filterset_params:
                value = filterset_params[key]
                if isinstance(value, list):
                    if len(value) == 1:
                        param = urlencode({key: value[0]})
                        params += param + "&"
                    else:
                        for v in value:
                            param = urlencode({key: v})
                            params += param + "&"
                else:
                    param = urlencode({key: value})
                    params += param + "&"
            params = params[:-1]  # Remove the last '&'
        return params


class AwesomeSearchModelAdmin(admin.ModelAdmin):
    """
    Subclass based on https://djangosnippets.org/snippets/2322/ allowing
    advanced filtering with https://github.com/alex/django-filter
    """

    def get_changelist(self, request, **kwargs):
        """Returns the ChangeList class for use on the changelist page."""
        return AwesomeSearchChangeList

    def changelist_view(self, request, extra_context=None, **kwargs):
        """
        FilterSet params must be removed from request within this function, or
        IncorrectLookupParameters exception will be raised.
        """
        # Copy request.GET for preserved filters.
        self.awesome_preserved_filters = request.GET.copy()
        # To remove filterset params from request, temporarily make
        # request.GET mutable
        request.GET._mutable = True
        self.filterset_exclude = request.GET.pop("_exclude", False)
        if hasattr(self, "filter_class"):
            # request = self._get_preserved_filters(request)
            # Get and delete filterset params
            # Reset filterset params every request
            self.get_filterset_params(request)
        # Restore immutability of request.GET
        request.GET._mutable = False
        return super().changelist_view(request, extra_context=extra_context)

    def get_preserved_filters(self, request):
        """
        Return the preserved filters querystring.
        """
        match = request.resolver_match
        if self.preserve_filters and match:
            opts = self.model._meta
            current_url = "%s:%s" % (match.app_name, match.url_name)
            changelist_url = "admin:%s_%s_changelist" % (
                opts.app_label,
                opts.model_name,
            )
            if current_url == changelist_url:
                # BEGIN CUSTOMIZATION #
                preserved_filters = self.awesome_preserved_filters.urlencode()
                # END CUSTOMIZATION #
            else:
                preserved_filters = request.GET.get("_changelist_filters")

            if preserved_filters:
                return urlencode({"_changelist_filters": preserved_filters})
        return ""

    #     def get_previous_request_from_session(self, request):
    #         match = request.resolver_match
    #         if self.preserve_filters and match:
    #             view_name = match.view_name
    #             if not request.GET:
    #                 if view_name in request.session:
    #                     query_string = request.session[view_name]
    #                     request.GET = QueryDict(query_string, mutable=True)
    #             else:
    #                 preserved_filters = request.GET.urlencode()
    #                 request.session[view_name] = preserved_filters
    #         return request

    def get_filterset_params(self, request):
        if hasattr(self, "filter_class"):
            # Does this matter?
            filter_class = self.filter_class(request=request)
            if hasattr(filter_class, "get_initial"):
                self.filterset_params = filter_class.get_initial()
            else:
                self.filterset_params = {}
            form = filter_class.form
            for field in form.fields:
                # Is it a RangeField, etc?
                if hasattr(form.fields[field], "fields"):
                    for index, _ in enumerate(form.fields[field].fields):
                        param = "{}_{}".format(field, index)
                        self.set_filterset_param(request, form, field, param)
                else:
                    param = field
                    self.set_filterset_param(request, form, field, param)

    def set_filterset_param(self, request, form, field, param):
        is_multiple = isinstance(form.fields[field], MultipleChoiceField) or isinstance(
            form.fields[field], ModelMultipleChoiceField
        )
        # Get list for multiple, or single value
        if is_multiple:
            value = request.GET.getlist(param)
            value = [v for v in value if v != ""]  # No blank params
        else:
            value = request.GET.get(param, None)
        # Set value
        if value:
            self.filterset_params[param] = value
        # Delete param every request
        if param in request.GET:
            del request.GET[param]

    def get_search_results(self, request, queryset, search_term):
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        # BEGIN CUSTOMIZATION #
        search_terms = self.get_search_terms(search_term)

        # END CUSTOMIZATION #

        # Apply keyword searches.
        def construct_search(field_name):
            if field_name.startswith("^"):
                return "%s__istartswith" % field_name[1:]
            elif field_name.startswith("="):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith("@"):
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name

        use_distinct = False
        search_fields = self.get_search_fields(request)

        # BEGIN CUSTOMIZATION #
        if search_terms:
            for search_term in search_terms:
                qs = self.model.objects.none()  # Create an empty queryset
                # END CUSTOMIZATION #
                if search_fields and search_term:
                    orm_lookups = [
                        construct_search(str(search_field))
                        for search_field in search_fields
                    ]
                    for bit in search_term.split():
                        or_queries = [
                            models.Q(**{orm_lookup: bit}) for orm_lookup in orm_lookups
                        ]

                        # BEGIN CUSTOMIZATION #
                        qs |= self.get_method_for_queryset(queryset)(
                            reduce(operator.or_, or_queries)
                        )
                        # END CUSTOMIZATION #

                    if not use_distinct:
                        for search_spec in orm_lookups:
                            if lookup_needs_distinct(self.opts, search_spec):
                                use_distinct = True
                                break

        # BEGIN CUSTOMIZATION #
        else:
            qs = queryset
        if hasattr(self, "filter_class") and hasattr(self, "filterset_params"):
            kwargs = {"request": request, "queryset": qs, "passed_validation": True}
            self.get_exclude(kwargs)
            filterset = self.filter_class(self.filterset_params, **kwargs)
            try:
                filterset = self.filter_class(self.filterset_params, **kwargs)
            except Exception:
                pass
            else:
                self.filterset = filterset
                qs = filterset.qs
        # END CUSTOMIZATION #
        return qs, use_distinct

    def get_exclude(self, kwargs):
        try:
            from .filters import SemanticExcludeAllFilterSet
        except ImportError:
            pass
        else:
            if issubclass(self.filter_class, SemanticExcludeAllFilterSet):
                kwargs["exclude"] = self.filterset_exclude

    def get_method_for_queryset(self, queryset):
        exclude = getattr(self, "filterset_exclude", False)
        if exclude:
            queryset = queryset.exclude
        else:
            queryset = queryset.filter
        return queryset

    def get_search_terms(self, search_term):
        search_terms = []
        ascii_space_separated = search_term.split(" ")
        jis_space_separated = search_term.split("\u3000")
        # Search ASCII for JIS
        for search_term in ascii_space_separated:
            s = search_term.split("\u3000")
            search_terms += s
        # Search JIS for ASCII
        for search_term in jis_space_separated:
            s = search_term.split(" ")
            search_terms += s
        # Remove whitespace, and empty strings
        search_terms = [s.strip().strip("\u3000") for s in search_terms if len(s)]
        # Search terms should be distinct
        search_terms = list(set(search_terms))
        return search_terms
