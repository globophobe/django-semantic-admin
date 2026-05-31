from django import forms, template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

BLANK_LABEL = "<label>&nbsp;</label>"
FIELD = '<div class="field">{}</div>'
FILTER_FIELD = '<div class="four wide field">{}</div>'
SPACER_FIELD = '<div class="four wide field semantic-admin-awesome-search-spacer"></div>'

register = template.Library()


def get_filterset(cl):
    return getattr(cl, "semantic_filterset", getattr(cl.model_admin, "filterset", None))


def has_filterset(cl):
    return get_filterset(cl) is not None


def should_show_search_field(cl):
    show_search_field = getattr(
        cl,
        "semantic_show_search_field",
        getattr(cl.model_admin, "show_search_field", True),
    )
    return bool(cl.search_fields and show_search_field)


def should_show_search_form(cl):
    filterset = get_filterset(cl)
    has_filter_fields = bool(filterset and filterset.form.fields)
    return should_show_search_field(cl) or has_filter_fields


def join_html(items):
    return mark_safe("".join(str(item) for item in items))


def format_fields(cl, fields):
    html = ""
    row = '<div class="fields semantic-admin-awesome-search-row">{}</div>'
    r = []
    for index, field in enumerate(fields):
        r.append(field)
        i = index + 1
        is_divisible_by_4 = not i % 4
        if is_divisible_by_4:
            html += format_html(row, join_html(r))
            r = []
    # Remaining fields. Keep the search action as the fourth slot.
    while len(r) < 3:
        r.append(SPACER_FIELD)
    search_button = format_search_button(cl)
    r.append(search_button)
    html += format_html(row, join_html(r))
    return html


def format_search_input(context, cl):
    search_var = context["search_var"]
    if getattr(cl, "search_help_text", None):
        return format_html(
            '''
            <input
                id="searchbar"
                type="text"
                name="{}"
                value="{}"
                aria-describedby="searchbar_helptext"
            />
        ''',
            search_var,
            cl.query,
        )
    return format_html(
        '''
            <input
                id="searchbar"
                type="text"
                name="{}"
                value="{}"
            />
        ''',
        search_var,
        cl.query,
    )


def format_search_field(context, cl):
    if not should_show_search_field(cl):
        return ""

    label = _("Search")
    search_label = format_html('<label for="searchbar">{}: </label>', label)
    search_input = format_search_input(context, cl)
    if has_filterset(cl):
        field = format_html("{}{}", search_label, search_input)
    else:
        field = format_html(
            '''
                <div class="ui action input">
                    {}
                    <button class="ui blue button" type="submit">
                        <i class="search icon"></i>{}
                    </button>
                </div>
            ''',
            search_input,
            label,
        )
    wrapper = FILTER_FIELD if has_filterset(cl) else FIELD
    return format_html(wrapper, field)


def format_search_button(cl):
    search_label = _("Search")
    search_button = format_html(
        '''
        <button class="ui fluid blue button" type="submit">
            <i class="search icon"></i> {}
        </button>
    ''',
        search_label,
    )
    if has_filterset(cl):
        return format_html(
            '''
            <div class="four wide field">
                <label>&nbsp;</label>{}
            </div>
        ''',
            search_button,
        )
    return format_html(FIELD, search_button)


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
    filterset = get_filterset(cl)
    if filterset:
        fields = []
        if search_field:
            fields.append(search_field)
        form = filterset.form
        for field in filterset.form:
            label = _(field.label.lower()).capitalize()
            if isinstance(form.fields[field.name].widget, forms.HiddenInput):
                f = format_html(
                    '''
                    <label for="{}">{}: </label>
                    <strong>{}</strong>
                    {}{}
                ''',
                    field.id_for_label,
                    label,
                    getattr(filterset, "email", ""),
                    field,
                    field.errors,
                )
            else:
                f = format_html(
                    '''
                    <label for="{}">{}: </label>
                    {}{}
                ''',
                    field.id_for_label,
                    label,
                    field,
                    field.errors,
                )
            f = format_html(FILTER_FIELD, f)
            fields.append(f)
        try:
            from semantic_admin.filters import SemanticExcludeAllFilterSet
        except ImportError:
            pass
        else:
            if isinstance(filterset, SemanticExcludeAllFilterSet):
                exclude_label = _("Exclude")
                checked = "checked" if getattr(cl.model_admin, "filterset_exclude", False) else ""
                exclude_checkbox = format_html(
                    '''
                    {}
                    <div class="ui checkbox">
                        <input
                            id="exclude"
                            type="checkbox"
                            tabindex="0"
                            class="hidden"
                            name="_exclude"
                            value="true"
                            {}
                        >
                        <label for="exclude">{}</label>
                    </div>
                ''',
                    mark_safe(BLANK_LABEL),
                    checked,
                    exclude_label,
                )
                f = format_html(FILTER_FIELD, exclude_checkbox)
                fields.append(f)
        html += format_fields(cl, fields)
    else:
        html = search_field
    return mark_safe(html)
