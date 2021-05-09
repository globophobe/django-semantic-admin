import types

from django.template.library import Library
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = Library()


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
