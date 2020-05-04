from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import cached_property
from django_react_streamfield.blocks import ChoiceBlock, ChooserBlock

from semantic_admin.widgets import SemanticAutocompleteChooser


class SemanticBlockMixin:
    @property
    def media(self):
        return forms.Media(js=["semantic_admin/semanticWidgets.js"])


class SemanticAutocompleteBlock(SemanticBlockMixin, ChooserBlock):
    def __init__(self, target_model, admin="admin", **kwargs):
        super().__init__(**kwargs)
        self.admin = admin
        self._target_model = target_model

    @cached_property
    def target_model(self):
        target = self._target_model
        if isinstance(target, str):
            app_label, model = target.split(".")
            ctype = ContentType.objects.get(app_label, model)
            target = ctype.model_class()
        return target

    @cached_property
    def widget(self):
        class AdminAutocomplete:
            def __init__(self, admin_site, model):
                self.name = admin_site
                self.model = model

        admin_autocomplete = AdminAutocomplete(self.admin, self.target_model)
        chooser = SemanticAutocompleteChooser(admin_autocomplete, admin_autocomplete)
        return chooser

    def render_form(self, *args, **kwargs):
        string = super().render_form(*args, **kwargs)
        return string + "<script>semanticChooser()</script>"


class SemanticChoiceBlock(SemanticBlockMixin, ChoiceBlock):
    def render_form(self, *args, **kwargs):
        string = super().render_form(*args, **kwargs)
        return string + "<script>semanticDropdown()</script>"
