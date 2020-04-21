from django_react_streamfield.blocks import ChoiceBlock


class SemanticChoiceBlock(ChoiceBlock):
    def render_form(self, value, prefix="", errors=None):
        string = super().render_form(value, prefix=prefix, errors=errors)
        return string + "<script>semanticDropdowns()</script>"
