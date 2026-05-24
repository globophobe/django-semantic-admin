import types

from django.template.library import Library
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = Library()


def _add_tag_classes(tag, classes):
    class_attr = 'class="'
    if class_attr in tag:
        return tag.replace(class_attr, f"{class_attr}{classes} ", 1)
    return tag.replace(">", f" class=\"{classes}\">", 1)


@register.filter(is_safe=True, needs_autoescape=True)
def semantic_help_text(value, autoescape=True):
    """Render generated help text with Semantic UI list classes."""
    if not value:
        return ""

    escaper = conditional_escape if autoescape else lambda x: x
    html = str(escaper(value))
    html = html.replace("<ul>", _add_tag_classes("<ul>", "ui bulleted list"))
    html = html.replace("<li>", _add_tag_classes("<li>", "item"))
    return mark_safe(html)


@register.filter(is_safe=True, needs_autoescape=True)
def semantic_error_list(value, autoescape=True):
    """Render Django form errors as a compact Semantic Admin error list."""
    if not value:
        return ""

    escaper = conditional_escape if autoescape else lambda x: x
    items = "".join(f'<li class="item">{escaper(error)}</li>' for error in value)
    return mark_safe(f'<ul class="ui bulleted list semantic-error-list">{items}</ul>')


@register.filter(is_safe=True, needs_autoescape=True)
def semantic_unordered_list(value, autoescape=True):
    """
    Recursively take a self-nested list and return an HTML unordered list --
    WITHOUT opening and closing <ul> tags.
    Assume the list is in the proper format. For example, if ``var`` contains:
    ``['States', ['Kansas', ['Lawrence', 'Topeka'], 'Illinois']]``, then
    ``{{ var|unordered_list }}`` returns::
        <div class="item">States
        <div class="ui bulleted list">
                <div class="item">Kansas</div>
                <div class="ui bulleted list">
                        <div class="item">Lawrence</div>
                        <div class="item">Topeka</div>
                </div>
                </div>
                <div class="item">Illinois</div>
        </div>
        </div>
    """
    if autoescape:
        escaper = conditional_escape
    else:

        def escaper(x):
            return x

    def walk_items(item_list):
        item_iterator = iter(item_list)
        try:
            item = next(item_iterator)
            while True:
                try:
                    next_item = next(item_iterator)
                except StopIteration:
                    yield item, None
                    break
                if isinstance(next_item, (list, tuple, types.GeneratorType)):
                    try:
                        iter(next_item)
                    except TypeError:
                        pass
                    else:
                        yield item, next_item
                        item = next(item_iterator)
                        continue
                yield item, None
                item = next_item
        except StopIteration:
            pass

    def list_formatter(item_list, tabs=1):
        indent = "\t" * tabs
        output = []
        for item, children in walk_items(item_list):
            sublist = ""
            if children:
                sublist = '\n%s<div class="ui bulleted list">\n%s\n%s</div>\n%s' % (
                    indent,
                    list_formatter(children, tabs + 1),
                    indent,
                    indent,
                )
            output.append(
                '%s<div class="item">%s%s</div>' % (indent, escaper(item), sublist)
            )
        return "\n".join(output)

    return mark_safe(list_formatter(value))
