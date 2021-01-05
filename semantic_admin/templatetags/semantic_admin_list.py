import datetime

from django import template
from django.contrib.admin.templatetags.admin_list import ResultList, _coerce_field_name
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import lookup_field
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import NoReverseMatch
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from semantic_admin.utils import semantic_display_for_field, semantic_display_for_value

register = template.Library()


def _semantic_boolean_icon(field_val):
    return format_html(
        '<i class="%s circle icon"></i>'
        % {True: "green check", False: "red times", None: "gray question"}[field_val]
    )


def semantic_items_for_result(cl, result, form):
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
                # BEGIN CUSTOMIZATION
                result_repr = semantic_display_for_value(
                    value, empty_value_display, boolean
                )
                # END CUSTOMIZATION
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
                    # BEGIN CUSTOMIZATION
                    result_repr = semantic_display_for_field(
                        value, f, empty_value_display
                    )
                    # END CUSTOMIZATION
                if isinstance(
                    f, (models.DateField, models.TimeField, models.ForeignKey)
                ):
                    row_classes.append("nowrap")
        row_class = mark_safe(' class="%s"' % " ".join(row_classes))
        # If list_display_links not defined, add the link tag to the first field
        if link_in_col(first, field_name, cl):

            # BEGIN CUSTOMIZATION
            table_tag = "td"
            # END CUSTOMIZATION

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
            # By default the fields come from ModelAdmin.list_editable, but if we pull
            # the fields out of the form instead of list_editable custom admins
            # can provide fields on a per request basis
            if (
                form
                and field_name in form.fields
                and not (
                    field_name == cl.model._meta.pk.name
                    and form[cl.model._meta.pk.name].is_hidden
                )
            ):

                # BEGIN CUSTOMIZATION
                field = form.fields[field_name]
                bf = form[field_name]
                if isinstance(field.widget, RelatedFieldWidgetWrapper):
                    bf_repr = str(bf.errors) + "&nbsp;" + str(bf)
                else:
                    bf_repr = str(bf.errors) + str(bf)
                result_repr = mark_safe(bf_repr)
                # END CUSTOMIZATION

            yield format_html("<td{}>{}</td>", row_class, result_repr)
    if form and not form[cl.model._meta.pk.name].is_hidden:
        yield format_html("<td>{}</td>", form[cl.model._meta.pk.name])


def semantic_results(cl):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            yield ResultList(form, semantic_items_for_result(cl, res, form))
    else:
        for res in cl.result_list:
            yield ResultList(None, semantic_items_for_result(cl, res, None))
