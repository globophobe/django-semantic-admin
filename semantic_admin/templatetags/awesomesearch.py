from django import forms, template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

BLANK_LABEL = "<label>&nbsp;</label>"
FIELD = '<div class="field">{}</div>'
COMPUTER_FIELD = '<div class="computer only field"></div>'

register = template.Library()

try:
    from django.utils.translation import gettext_lazy as _  # Django >= 4
except ImportError:
    from django.utils.translation import ugettext_lazy as _


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
        filterset = cl.model_admin.filterset
        form = filterset.form
        for field in filterset.form:
            # WTF
            label = _(field.label.lower()).capitalize()
            if isinstance(form.fields[field.name].widget, forms.HiddenInput):
                f = f"""
                    <label for="{field.id_for_label}">{label}: </label>
                    <strong>{filterset.email}</strong>
                    {field}{field.errors}
                """
            else:
                format_dict = dict(
                    field_id=field.id_for_label,
                    label=label,
                    field=field,
                    errors=field.errors,
                )
                f = filter_field.format(**format_dict)
            f = FIELD.format(f)
            fields.append(f)
        try:
            from semantic_admin.filters import SemanticExcludeAllFilterSet
        except ImportError:
            pass
        else:
            if isinstance(cl.model_admin.filterset, SemanticExcludeAllFilterSet):
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
    return format_html(mark_safe(html))
