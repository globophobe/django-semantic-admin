from django import forms
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import cached_property
from django_react_streamfield.blocks import (
    BooleanBlock,
    ChoiceBlock,
    ChooserBlock,
    FieldBlock,
)

from semantic_admin.widgets import SemanticAutocompleteChooser, SemanticCheckboxInput


class SemanticMediaMixin:
    @property
    def media(self):
        return forms.Media(js=["semantic_admin/semanticWidgets.js"])


class SemanticAutocompleteBlock(SemanticMediaMixin, ChooserBlock):
    def __init__(self, target_model, admin="admin", **kwargs):
        super().__init__(**kwargs)
        self.admin = admin
        self._target_model = target_model

    @cached_property
    def target_model(self):
        target = self._target_model
        if isinstance(target, str):
            app_label, model = target.split(".")
            ctype = ContentType.objects.get(app_label=app_label, model=model.lower())
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
        return string + "<script>semanticChooser();</script>"


class SemanticChoiceBlock(SemanticMediaMixin, ChoiceBlock):
    def render_form(self, *args, **kwargs):
        string = super().render_form(*args, **kwargs)
        return string + "<script>semanticDropdown();</script>"


class SemanticBooleanBlock(SemanticMediaMixin, FieldBlock):
    def __init__(self, help_text=None, **kwargs):
        # NOTE: As with forms.BooleanField, the default of required=True means that the
        # checkbox must be ticked to pass validation (i.e. it's equivalent to an "I
        # agree to the terms and conditions" box). To get the conventional yes/no
        # behaviour, you must explicitly pass required=False.
        self.field = forms.BooleanField(
            required=kwargs["required"],
            help_text=help_text,
            widget=SemanticCheckboxInput(),
        )
        super().__init__(**kwargs)

    def render_form(self, *args, **kwargs):
        string = super().render_form(*args, **kwargs)
        return string + "<script>semanticCheckbox();</script>"

    def deconstruct(self):
        # As the sole purpose of this is to override the visual appearance, deconstruct
        # as BooleanBlock.
        name = BooleanBlock.__name__
        path = f"django_react_streamfield.blocks.{name}"
        return (path, self._constructor_args[0], self._constructor_args[1])
