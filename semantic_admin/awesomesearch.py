from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
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
        params = ""
        if filterset_params:
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
        if hasattr(self, "filter_class"):
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
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term
        )
        if hasattr(self, "filter_class") and hasattr(self, "filterset_params"):
            kwargs = {
                "request": request,
                "queryset": queryset,
                "passed_validation": True,
            }
            self.filterset = filterset = self.filter_class(
                self.filterset_params, **kwargs
            )
            queryset = filterset.qs
        return queryset, may_have_duplicates
