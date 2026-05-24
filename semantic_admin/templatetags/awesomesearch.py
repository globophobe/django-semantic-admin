from django import forms, template
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

BLANK_LABEL = "<label>&nbsp;</label>"
FIELD = '<div class="field">{}</div>'
FILTER_FIELD = '<div class="four wide field">{}</div>'
SPACER_FIELD = '<div class="four wide field semantic-admin-awesome-search-spacer"></div>'

register = template.Library()


def should_show_search_field(cl):
    return bool(cl.search_fields and getattr(cl.model_admin, "show_search_field", True))


def should_show_search_form(cl):
    has_filter_fields = False
    if hasattr(cl.model_admin, "filterset"):
        has_filter_fields = bool(cl.model_admin.filterset.form.fields)
    return should_show_search_field(cl) or has_filter_fields


def format_fields(cl, fields):
    html = ""
    row = '<div class="fields semantic-admin-awesome-search-row">{}</div>'
    r = []
    for index, field in enumerate(fields):
        r.append(field)
        i = index + 1
        is_divisible_by_4 = not i % 4
        if is_divisible_by_4:
            html += row.format("".join(r))
            r = []
    # Remaining fields. Keep the search action as the fourth slot.
    while len(r) < 3:
        r.append(SPACER_FIELD)
    search_button = format_search_button(cl)
    r.append(search_button)
    html += row.format("".join(r))
    return html


def format_search_field(context, cl):
    field = ""
    if should_show_search_field(cl):
        label = _("Search")
        search_var = context["search_var"]
        search_label = f'<label for="searchbar">{label}: </label>'
        # Add aria-describedby for search help text
        aria_describedby = ""
        if getattr(cl, "search_help_text", None):
            aria_describedby = ' aria-describedby="searchbar_helptext"'
        search_input = f"""
            <input
                id="searchbar"
                type="text"
                name="{search_var}"
                value="{cl.query}"{aria_describedby}
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
        wrapper = FILTER_FIELD if hasattr(cl.model_admin, "filterset") else FIELD
        return wrapper.format(field)
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
            <div class="four wide field">
                {BLANK_LABEL}{search_button}
            </div>
        """
    else:
        html = FIELD.format(search_button)
    return html


@register.simple_tag
def show_search_field(cl):
    return should_show_search_field(cl)


@register.simple_tag
def awesomesearch_show_search_form(cl):
    return should_show_search_form(cl)


@register.simple_tag(takes_context=True)
def search_fields(context, cl):
    html = ""
    search_field = format_search_field(context, cl)
    if hasattr(cl.model_admin, "filterset"):
        fields = []
        if search_field:
            fields.append(search_field)
        filter_field = """
            <label for="{field_id}">{label}: </label>
            {field}{errors}
        """
        filterset = cl.model_admin.filterset
        form = filterset.form
        for field in filterset.form:
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
            f = FILTER_FIELD.format(f)
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
                f = FILTER_FIELD.format(exclude_checkbox)
                fields.append(f)
        html += format_fields(cl, fields)
    else:
        html = search_field
    return mark_safe(html)
