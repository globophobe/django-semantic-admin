import datetime

from django import template
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.templatetags.admin_list import (
    DOT,
    ResultList,
    _coerce_field_name,
    label_for_field,
    result_hidden_fields,
)
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import (
    display_for_field,
    display_for_value,
    lookup_field,
)
from django.contrib.admin.views.main import ORDER_VAR, PAGE_VAR
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import NoReverseMatch, resolve, reverse
from django.utils.html import format_html, mark_safe
from django.utils.translation import ugettext_lazy as _

try:
    from semantic_admin.filters import ExcludeAllFilterSet
except ImportError:

    class ExcludeAllFilterSet:
        pass


register = template.Library()

BLANK_LABEL = "<label>&nbsp;</label>"
FIELD = '<div class="field">{}</div>'
COMPUTER_FIELD = '<div class="computer only field"></div>'


@register.simple_tag(takes_context=True)
def debug(context):
    if settings.DEBUG:
        import pdb

        pdb.set_trace()


def format_fields(cl, fields):
    html = ""
    row = '<div class="equal width fields">{}</div>'
    r = []
    for index, field in enumerate(fields):
        r.append(field)
        i = index + 1
        is_divisible_by_4 = not i % 4
        if is_divisible_by_4:
            html += row.format("".join(r))
            r = []
    # Remaining fields.
    while len(r) < 3:
        r.append(COMPUTER_FIELD)
    search_button = format_search_button(cl)
    r.append(search_button)
    html += row.format("".join(r))
    return html


def format_search_button(cl):
    html = ""
    search_label = _("Search")
    search_button = f"""
        <button class="ui fluid blue button" type="submit">
            <i class="search icon"></i> {search_label}
        </button>
    """
    if hasattr(cl.model_admin, "filterset"):
        html = f"""
            <div class="field">
                {BLANK_LABEL}{search_button}
            </div>
        """
    else:
        html = FIELD.format(search_button)
    return html


def format_search_field(context, cl):
    field = ""
    if len(cl.search_fields):
        label = _("Search")
        search_var = context["search_var"]
        search_label = f'<label for="searchbar">{label}: </label>'
        search_input = f"""
            <input
                id="searchbar"
                type="text"
                name="{search_var}"
                value="{cl.query}"
            />
        """
        if hasattr(cl.model_admin, "filterset"):
            field = f"{search_label}{search_input}"
        else:
            field = f"""
                <div class="ui action input">
                    {search_input}
                    <button class="ui blue button" type="submit">
                        <i class="search icon"></i>{label}
                    </button>
                </div>
            """
        return FIELD.format(field)
    else:
        return ""


@register.simple_tag(takes_context=True)
def search_fields(context, cl):
    html = ""
    search_field = format_search_field(context, cl)
    if hasattr(cl.model_admin, "filterset"):
        fields = [search_field]
        filter_field = """
            <label for="{field_id}">{label}: </label>
            {field}{errors}
        """
        for field in cl.model_admin.filterset.form:
            # WTF
            label = _(field.label.lower())
            format_dict = dict(
                field_id=field.id_for_label,
                label=label,
                field=field,
                errors=field.errors,
            )
            f = filter_field.format(**format_dict)
            f = FIELD.format(f)
            fields.append(f)
        if isinstance(cl.model_admin.filterset, ExcludeAllFilterSet):
            exclude_label = _("Exclude")
            checked = cl.model_admin.filterset_exclude
            exclude_checkbox = f"""
                {BLANK_LABEL}
                <div class="ui checkbox">
                    <input
                        id="exclude"
                        type="checkbox"
                        tabindex="0"
                        class="hidden"
                        name="_exclude"
                        value="true"
                        {checked}
                    >
                    <label for="exclude">{exclude_label}</label>
                </div>
            """
            f = FIELD.format(exclude_checkbox)
            fields.append(f)
        html += format_fields(cl, fields)
    else:
        html = search_field
    return mark_safe(html)


def items_for_result(cl, result, form):
    """
    Generate the actual list of data.
    """

    def link_in_col(is_first, field_name, cl):
        if cl.list_display_links is None:
            return False
        if is_first and not cl.list_display_links:
            return True
        return field_name in cl.list_display_links

    first = True
    pk = cl.lookup_opts.pk.attname
    for field_index, field_name in enumerate(cl.list_display):
        empty_value_display = cl.model_admin.get_empty_value_display()
        row_classes = ["field-%s" % _coerce_field_name(field_name, field_index)]
        try:
            f, attr, value = lookup_field(field_name, result, cl.model_admin)
        except ObjectDoesNotExist:
            result_repr = empty_value_display
        else:
            empty_value_display = getattr(
                attr, "empty_value_display", empty_value_display
            )
            if f is None or f.auto_created:
                if field_name == "action_checkbox":
                    row_classes = ["action-checkbox"]
                boolean = getattr(attr, "boolean", False)
                result_repr = display_for_value(value, empty_value_display, boolean)
                if isinstance(value, (datetime.date, datetime.time)):
                    row_classes.append("nowrap")
            else:
                if isinstance(f.remote_field, models.ManyToOneRel):
                    field_val = getattr(result, f.name)
                    if field_val is None:
                        result_repr = empty_value_display
                    else:
                        result_repr = field_val
                else:
                    result_repr = display_for_field(value, f, empty_value_display)
                if isinstance(
                    f, (models.DateField, models.TimeField, models.ForeignKey)
                ):
                    row_classes.append("nowrap")

        # BEGIN CUSTOMIZATION #
        # WTF Unicode?
        if not result_repr:
            if str(result_repr) == "":
                result_repr = mark_safe("&nbsp;")
        # END CUSTOMIZATION #

        row_class = mark_safe(' class="%s"' % " ".join(row_classes))
        # If list_display_links not defined, add the link tag to the first
        # field
        if link_in_col(first, field_name, cl):

            # BEGIN CUSTOMIZATION #
            table_tag = "td"  # if first else 'td'
            # END CUSTOMIZATION #

            first = False

            # Display link to the result's change_view if the url exists, else
            # display just the result's representation.
            try:
                url = cl.url_for_result(result)
            except NoReverseMatch:
                link_or_text = result_repr
            else:
                url = add_preserved_filters(
                    {"preserved_filters": cl.preserved_filters, "opts": cl.opts}, url
                )
                # Convert the pk to something that can be used in Javascript.
                # Problem cases are non-ASCII strings.
                if cl.to_field:
                    attr = str(cl.to_field)
                else:
                    attr = pk
                value = result.serializable_value(attr)
                link_or_text = format_html(
                    '<a href="{}"{}>{}</a>',
                    url,
                    format_html(' data-popup-opener="{}"', value)
                    if cl.is_popup
                    else "",
                    result_repr,
                )

            yield format_html(
                "<{}{}>{}</{}>", table_tag, row_class, link_or_text, table_tag
            )
        else:
            # By default the fields come from ModelAdmin.list_editable, but if
            # we pull the fields out of the form instead of list_editable
            # custom admins can provide fields on a per request basis
            if (
                form
                and field_name in form.fields
                and not (
                    field_name == cl.model._meta.pk.name
                    and form[cl.model._meta.pk.name].is_hidden
                )
            ):
                bf = form[field_name]
                result_repr = mark_safe(str(bf.errors) + str(bf))
            yield format_html("<td{}>{}</td>", row_class, result_repr)
    if form and not form[cl.model._meta.pk.name].is_hidden:
        yield format_html("<td>{}</td>", form[cl.model._meta.pk.name])


def results(cl):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            yield ResultList(form, items_for_result(cl, res, form))
    else:
        for res in cl.result_list:
            yield ResultList(None, items_for_result(cl, res, None))


def has_action_checkbox(cl):
    for i, field_name in enumerate(cl.list_display):
        text, attr = label_for_field(
            field_name, cl.model, model_admin=cl.model_admin, return_attr=True
        )
        if attr:
            field_name = _coerce_field_name(field_name, i)
            # Potentially not sortable

            # if the field is the action checkbox: no sorting and special class
            if field_name == "action_checkbox":
                return True


def result_headers(cl):
    """
    Generate the list column headers.
    """
    ordering_field_columns = cl.get_ordering_field_columns()
    for i, field_name in enumerate(cl.list_display):
        text, attr = label_for_field(
            field_name, cl.model, model_admin=cl.model_admin, return_attr=True
        )
        if attr:
            field_name = _coerce_field_name(field_name, i)
            # Potentially not sortable

            # if the field is the action checkbox: no sorting and special class
            if field_name == "action_checkbox":
                yield {
                    "text": mark_safe(text),
                    "class_attrib": mark_safe("action-checkbox-column"),
                    "sortable": False,
                }
                continue

            admin_order_field = getattr(attr, "admin_order_field", None)
            if not admin_order_field:
                # Not sortable
                yield {
                    "text": text,
                    "class_attrib": format_html("column-{}", field_name),
                    "sortable": False,
                }
                continue

        # OK, it is sortable if we got this far
        th_classes = ["sortable", "column-{}".format(field_name)]
        order_type = ""
        new_order_type = "asc"
        sort_priority = 0
        sorted = False
        # Is it currently being sorted on?
        if i in ordering_field_columns:
            sorted = True
            order_type = ordering_field_columns.get(i).lower()
            sort_priority = list(ordering_field_columns).index(i) + 1
            th_classes.append("sorted %sending" % order_type)
            new_order_type = {"asc": "desc", "desc": "asc"}[order_type]

        # build new ordering param
        o_list_primary = []  # URL for making this field the primary sort
        o_list_remove = []  # URL for removing this field from sort
        o_list_toggle = []  # URL for toggling order type for this field

        def make_qs_param(t, n):
            return ("-" if t == "desc" else "") + str(n)

        for j, ot in ordering_field_columns.items():
            if j == i:  # Same column
                param = make_qs_param(new_order_type, j)
                # We want clicking on this header to bring the ordering to the
                # front
                o_list_primary.insert(0, param)
                o_list_toggle.append(param)
                # o_list_remove - omit
            else:
                param = make_qs_param(ot, j)
                o_list_primary.append(param)
                o_list_toggle.append(param)
                o_list_remove.append(param)

        if i not in ordering_field_columns:
            o_list_primary.insert(0, make_qs_param(new_order_type, i))

        yield {
            "text": text,
            "sortable": True,
            "sorted": sorted,
            "ascending": order_type == "asc",
            "sort_priority": sort_priority,
            "url_primary": cl.get_query_string({ORDER_VAR: ".".join(o_list_primary)}),
            "url_remove": cl.get_query_string({ORDER_VAR: ".".join(o_list_remove)}),
            "url_toggle": cl.get_query_string({ORDER_VAR: ".".join(o_list_toggle)}),
            "class_attrib": format_html("{}", " ".join(th_classes))
            if th_classes
            else "",
        }


@register.inclusion_tag("admin/change_list_results.html")
def semantic_result_list(cl):
    """
    Display the headers and data list together.
    """
    headers = list(result_headers(cl))
    num_sorted_fields = 0
    for h in headers:
        if h["sortable"] and h["sorted"]:
            num_sorted_fields += 1
    return {
        "cl": cl,
        "opts": cl.model_admin.opts,  # WTF?!
        "has_action_checkbox": has_action_checkbox(cl),
        "result_hidden_fields": list(result_hidden_fields(cl)),
        "result_headers": headers,
        "num_sorted_fields": num_sorted_fields,
        "results": list(results(cl)),
    }


@register.simple_tag
def semantic_paginator_number(cl, i):
    """
    Generate an individual page index link in a paginated list.
    """
    if i == DOT:
        return mark_safe('<span class="item">... </span>')
    elif i == cl.page_num:
        return format_html('<span class="this-page item active">{}</span> ', i + 1)
    else:
        return format_html(
            '<a href="{}" class="item{}">{}</a> ',
            cl.get_query_string({PAGE_VAR: i}),
            mark_safe(" end" if i == cl.paginator.num_pages - 1 else ""),
            i + 1,
        )


def get_semantic_sidebar(app_list, current_app):
    semantic_sidebar = getattr(settings, "SEMANTIC_SIDEBAR", None)
    if semantic_sidebar:
        ordered = []
        for app_label in semantic_sidebar:
            for app in app_list:
                is_current = app["app_label"] == current_app
                app["is_current"] = is_current
                if app_label == app["app_label"]:
                    ordered.append(app)
        app_list = ordered
    return app_list


def get_app_label(resolver_match):
    if "app_label" in resolver_match.kwargs:
        return resolver_match.kwargs.get("app_label")
    else:
        # Reconstruct from url_name.
        url_name = resolver_match.url_name
        # Exclude model and action.
        parts = url_name.split("_")[:-2]
        # Return parts.
        return "_".join(parts)


@register.simple_tag(takes_context=True)
def get_app_list(context):
    request = context["request"]
    resolver_match = resolve(request.path_info)
    admin_name = resolver_match.namespace
    current_app = get_app_label(resolver_match)
    admin_site = get_admin_site(admin_name)
    app_list = admin_site.get_app_list(request)
    return get_semantic_sidebar(app_list, current_app)


def get_admin_site(current_app):
    try:
        resolver_match = resolve(reverse("%s:index" % current_app))
        for func_closure in resolver_match.func.func_closure:
            if isinstance(func_closure.cell_contents, AdminSite):
                return func_closure.cell_contents
    except Exception:
        pass
    return admin.site


def get_admin_url(request, admin_site):
    try:
        url = "{}:index".format(admin_site)
        url = reverse(url)
    except Exception:
        pass
    else:
        return url


@register.simple_tag(takes_context=True)
def admin_apps(context):
    return get_app_list(context)
