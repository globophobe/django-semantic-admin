from typing import Optional, Tuple, Type

from django.contrib import admin, messages
from django.contrib.admin import helpers
from django.contrib.admin.options import IncorrectLookupParameters, csrf_protect_m
from django.contrib.admin.utils import model_ngettext
from django.contrib.admin.views.main import ChangeList
from django.core.exceptions import PermissionDenied
from django.db import router, transaction
from django.db.models import QuerySet
from django.forms import Form, ModelMultipleChoiceField
from django.forms.fields import MultipleChoiceField
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.response import SimpleTemplateResponse, TemplateResponse
from django.utils.http import urlencode
from django.utils.translation import ngettext
from django_filters import FilterSet

try:
    from django.utils.translation import gettext_lazy as _  # Django >= 4
except ImportError:
    from django.utils.translation import ugettext_lazy as _


class AwesomeSearchChangeList(ChangeList):
    """Awesome search change list"""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize"""
        super().__init__(*args, **kwargs)
        try:
            request = args[0]
        except IndexError:
            pass
        else:
            # WTF? Wasn't this already set.
            self.full_result_count = self.model_admin.get_queryset(request).count()

    def get_query_string(
        self, new_params: Optional[dict] = None, remove: Optional[str] = None
    ) -> str:
        """Get query string"""
        params = super().get_query_string(new_params=new_params, remove=remove)
        filterset_params = self.get_filterset_params()
        if filterset_params:
            if len(params) > 1:
                params += "&"
            params += filterset_params
        return params

    def get_filterset_params(self) -> str:
        """Get filterset params"""
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

    def get_filterset_class(self) -> Optional[FilterSet]:
        """Get filterset class"""
        if hasattr(self, "filter_class"):
            return self.filter_class
        elif hasattr(self, "filterset_class"):
            return self.filterset_class

    def get_changelist(
        self, request: HttpRequest, **kwargs
    ) -> Type[AwesomeSearchChangeList]:
        """Returns the ChangeList class for use on the changelist page."""
        return AwesomeSearchChangeList

    @csrf_protect_m
    def changelist_view(
        self, request: HttpRequest, extra_context: Optional[dict] = None, **kwargs
    ) -> HttpResponse:
        """
        FilterSet params must be removed from request within this function, or
        IncorrectLookupParameters exception will be raised.
        """
        # BEGIN CUSTOMIZATION
        # Copy request.GET for preserved filters.
        self.awesome_preserved_filters = request.GET.copy()
        # To remove filterset params from request, temporarily make
        # request.GET mutable
        request.GET._mutable = True
        if self.get_filterset_class():
            # Reset filterset params every request
            self.get_filterset_params(request)
        # Restore immutability of request.GET
        request.GET._mutable = False
        # END CUSTOMIZATION

        from django.contrib.admin.views.main import ERROR_FLAG

        app_label = self.opts.app_label
        if not self.has_view_or_change_permission(request):
            raise PermissionDenied

        try:
            cl = self.get_changelist_instance(request)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given
            # and the 'invalid=1' parameter was already in the query string,
            # something is screwed up with the database, so display an error
            # page.
            if ERROR_FLAG in request.GET:
                return SimpleTemplateResponse(
                    "admin/invalid_setup.html",
                    {
                        "title": _("Database error"),
                    },
                )
            return HttpResponseRedirect(request.path + "?" + ERROR_FLAG + "=1")

        # If the request was POSTed, this might be a bulk action or a bulk
        # edit. Try to look up an action or confirmation first, but if this
        # isn't an action the POST will fall through to the bulk edit check,
        # below.
        action_failed = False
        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

        actions = self.get_actions(request)
        # Actions with no confirmation
        if (
            actions
            and request.method == "POST"
            and "index" in request.POST
            and "_save" not in request.POST
        ):
            if selected:
                response = self.response_action(
                    request, queryset=cl.get_queryset(request)
                )
                if response:
                    return response
                else:
                    action_failed = True
            else:
                msg = _(
                    "Items must be selected in order to perform "
                    "actions on them. No items have been changed."
                )
                self.message_user(request, msg, messages.WARNING)
                action_failed = True

        # Actions with confirmation
        if (
            actions
            and request.method == "POST"
            and helpers.ACTION_CHECKBOX_NAME in request.POST
            and "index" not in request.POST
            and "_save" not in request.POST
        ):
            if selected:
                response = self.response_action(
                    request, queryset=cl.get_queryset(request)
                )
                if response:
                    return response
                else:
                    action_failed = True

        if action_failed:
            # Redirect back to the changelist page to avoid resubmitting the
            # form if the user refreshes the browser or uses the "No, take
            # me back" button on the action confirmation page.
            return HttpResponseRedirect(request.get_full_path())

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if request.method == "POST" and cl.list_editable and "_save" in request.POST:
            if not self.has_change_permission(request):
                raise PermissionDenied
            FormSet = self.get_changelist_formset(request)
            modified_objects = self._get_list_editable_queryset(
                request, FormSet.get_default_prefix()
            )
            formset = cl.formset = FormSet(
                request.POST, request.FILES, queryset=modified_objects
            )
            if formset.is_valid():
                changecount = 0
                with transaction.atomic(using=router.db_for_write(self.model)):
                    for form in formset.forms:
                        if form.has_changed():
                            obj = self.save_form(request, form, change=True)
                            self.save_model(request, obj, form, change=True)
                            self.save_related(request, form, formsets=[], change=True)
                            change_msg = self.construct_change_message(
                                request, form, None
                            )
                            self.log_change(request, obj, change_msg)
                            changecount += 1
                if changecount:
                    msg = ngettext(
                        "%(count)s %(name)s was changed successfully.",
                        "%(count)s %(name)s were changed successfully.",
                        changecount,
                    ) % {
                        "count": changecount,
                        "name": model_ngettext(self.opts, changecount),
                    }
                    self.message_user(request, msg, messages.SUCCESS)

                return HttpResponseRedirect(request.get_full_path())

        # Handle GET -- construct a formset for display.
        elif cl.list_editable and self.has_change_permission(request):
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)

        # Build the list of media to be used by the formset.
        if formset:
            media = self.media + formset.media
        else:
            media = self.media

        # Build the action form and populate it with available actions.
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields["action"].choices = self.get_action_choices(request)
            media += action_form.media
        else:
            action_form = None

        selection_note_all = ngettext(
            "%(total_count)s selected", "All %(total_count)s selected", cl.result_count
        )

        context = {
            **self.admin_site.each_context(request),
            "module_name": str(self.opts.verbose_name_plural),
            "selection_note": _("0 of %(cnt)s selected") % {"cnt": len(cl.result_list)},
            "selection_note_all": selection_note_all % {"total_count": cl.result_count},
            "title": cl.title,
            "subtitle": None,
            "is_popup": cl.is_popup,
            "to_field": cl.to_field,
            "cl": cl,
            "media": media,
            "has_add_permission": self.has_add_permission(request),
            "opts": cl.opts,
            "action_form": action_form,
            "actions_on_top": self.actions_on_top,
            "actions_on_bottom": self.actions_on_bottom,
            "actions_selection_counter": self.actions_selection_counter,
            "preserved_filters": self.get_preserved_filters(request),
            **(extra_context or {}),
        }

        request.current_app = self.admin_site.name

        # BEGIN CUSTOMIZATION
        if hasattr(self, "semantic_header"):
            context["semantic_header"] = self.semantic_header(cl.result_list)
        # END CUSTOMIZATION

        return TemplateResponse(
            request,
            self.change_list_template
            or [
                "admin/%s/%s/change_list.html"  # noqa: UP031
                % (app_label, self.opts.model_name),
                "admin/%s/change_list.html" % app_label,
                "admin/change_list.html",
            ],
            context,
        )

    def get_preserved_filters(self, request: HttpRequest) -> str:
        """Return the preserved filters querystring."""
        match = request.resolver_match
        if self.preserve_filters and match:
            opts = self.model._meta
            current_url = "%s:%s" % (match.app_name, match.url_name)  # noqa: UP031
            changelist_url = "admin:%s_%s_changelist" % (  # noqa: UP031
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

    def get_filterset_params(self, request: HttpRequest) -> None:
        """Get filterset params"""
        filterset_class = self.get_filterset_class()
        if filterset_class:
            filterset = filterset_class(request=request)
            if hasattr(filterset, "get_initial"):
                self.filterset_params = filterset.get_initial()
            else:
                self.filterset_params = {}
            form = filterset.form
            for field in form.fields:
                # Is it a RangeField, etc?
                if hasattr(form.fields[field], "fields"):
                    for index, _ in enumerate(form.fields[field].fields):
                        param = "{}_{}".format(field, index)
                        self.set_filterset_param(request, form, field, param)
                else:
                    param = field
                    self.set_filterset_param(request, form, field, param)

    def set_filterset_param(
        self, request: HttpRequest, form: Form, field: str, param: str
    ) -> None:
        """Set filterset param"""
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

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet, search_term: str
    ) -> Tuple[QuerySet, bool]:
        """
        Returns a tuple containing a queryset to implement the search,
        and a boolean indicating if the results may contain duplicates.
        """
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term
        )
        filterset_class = self.get_filterset_class()
        if filterset_class and hasattr(self, "filterset_params"):
            kwargs = {
                "request": request,
                "queryset": queryset,
                "passed_validation": True,
            }
            self.filterset = filterset_class(self.filterset_params, **kwargs)
            queryset = self.filterset.qs
        return queryset, may_have_duplicates
