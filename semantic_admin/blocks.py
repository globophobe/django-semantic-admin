from django_react_streamfield.blocks import ChoiceBlock


class SemanticChoiceBlock(ChoiceBlock):
    def render_form(self, *args, **kwargs):
        string = super().render_form(*args, **kwargs)
        return string + "<script>semanticDropdowns()</script>"
