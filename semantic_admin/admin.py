import copy
from functools import partial

from django import forms
from django.contrib.admin import helpers, widgets
from django.contrib.admin.options import (
    BaseModelAdmin,
    StackedInline,
    TabularInline,
    get_ul_class,
)
from django.db import models
from django.forms.models import (
    modelform_defines_fields,
    modelform_factory,
    modelformset_factory,
)
from django.utils.html import format_html

from semantic_admin.widgets import (
    SemanticActionCheckboxInput,
    SemanticAutocompleteSelect,
    SemanticAutocompleteSelectMultiple,
    SemanticChangelistCheckboxInput,
    SemanticCheckboxInput,
    SemanticDateInput,
    SemanticDateTimeInput,
    SemanticEmailInput,
    SemanticFileInput,
    SemanticImageInput,
    SemanticNumberInput,
    SemanticRadioSelect,
    SemanticSelect,
    SemanticSelectMultiple,
    SemanticTextarea,
    SemanticTextInput,
    SemanticTimeInput,
    SemanticURLInput,
)

from .awesomesearch import AwesomeSearchModelAdmin
from .helpers import SemanticActionForm
from .views.autocomplete import SemanticAutocompleteJsonView

try:
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    from django.utils.translation import gettext_lazy as _

SEMANTIC_FORMFIELD_FOR_DBFIELD_DEFAULTS = {
    models.DateTimeField: {"widget": SemanticDateTimeInput},
    models.DateField: {"widget": SemanticDateInput},
    models.TimeField: {"widget": SemanticTimeInput},
    models.TextField: {"widget": SemanticTextarea},
    models.URLField: {"widget": SemanticURLInput},
    # TODO
    models.IntegerField: {"widget": SemanticNumberInput},
    models.BigIntegerField: {"widget": SemanticNumberInput},
    # END TODO
    models.CharField: {"widget": SemanticTextInput},
    models.ImageField: {"widget": SemanticImageInput},
    models.FileField: {"widget": SemanticFileInput},
    models.EmailField: {"widget": SemanticEmailInput},
    models.UUIDField: {"widget": SemanticTextInput},
    models.BooleanField: {"widget": SemanticCheckboxInput},
}


class SemanticBaseModelAdmin(BaseModelAdmin):  # type: ignore
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Simply overwrite
        overrides = copy.deepcopy(SEMANTIC_FORMFIELD_FOR_DBFIELD_DEFAULTS)
        for k, v in overrides.items():
            self.formfield_overrides.setdefault(k, {}).update(v)
        self.formfield_overrides = overrides

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Get a form Field for a database Field that has declared choices.
        """
        # If the field is named as a radio_field, use a RadioSelect
        if db_field.name in self.radio_fields:
            # Avoid stomping on custom widget/choices arguments.
            if "widget" not in kwargs:

                # BEGIN CUSTOMIZATION
                kwargs["widget"] = SemanticRadioSelect(
                    attrs={
                        "class": get_ul_class(self.radio_fields[db_field.name]),
                    }
                )
                # END CUSTOMIZATION

            if "choices" not in kwargs:
                kwargs["choices"] = db_field.get_choices(
                    include_blank=db_field.blank, blank_choice=[("", _("None"))]
                )

        # BEGIN CUSTOMIZATION
        if "widget" not in kwargs:
            kwargs["widget"] = SemanticSelect()
        # END CUSTOMIZATION

        return db_field.formfield(**kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        db = kwargs.get("using")

        if db_field.name in self.get_autocomplete_fields(request):
            # BEGIN CUSTOMIZATION

            kwargs["widget"] = SemanticAutocompleteSelect(
                db_field, self.admin_site, using=db
            )

            # END CUSTOMIZATION

        elif db_field.name in self.raw_id_fields:
            # TODO
            kwargs["widget"] = widgets.ForeignKeyRawIdWidget(
                db_field.remote_field, self.admin_site, using=db
            )
        elif db_field.name in self.radio_fields:
            kwargs["widget"] = SemanticRadioSelect(
                attrs={"class": get_ul_class(self.radio_fields[db_field.name])}
            )
            kwargs["empty_label"] = _("None") if db_field.blank else None

        if "queryset" not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs["queryset"] = queryset

        # BEGIN CUSTOMIZATION
        if "widget" not in kwargs:
            kwargs["widget"] = SemanticSelect()
        # END CUSTOMIZATION

        return db_field.formfield(**kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.
        """
        # If it uses an intermediary model that isn't auto created, don't show
        # a field in admin.
        if not db_field.remote_field.through._meta.auto_created:
            return None
        db = kwargs.get("using")

        if "widget" not in kwargs:
            autocomplete_fields = self.get_autocomplete_fields(request)
            if db_field.name in autocomplete_fields:

                # BEGIN CUSTOMIZATION
                kwargs["widget"] = SemanticAutocompleteSelectMultiple(
                    db_field,
                    self.admin_site,
                    using=db,
                )
                # END CUSTOMIZATION

            elif db_field.name in self.raw_id_fields:
                kwargs["widget"] = widgets.ManyToManyRawIdWidget(
                    db_field.remote_field,
                    self.admin_site,
                    using=db,
                )
            elif db_field.name in [*self.filter_vertical, *self.filter_horizontal]:
                # TODO
                kwargs["widget"] = widgets.FilteredSelectMultiple(
                    db_field.verbose_name, db_field.name in self.filter_vertical
                )
        if "queryset" not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs["queryset"] = queryset

        # BEGIN CUSTOMIZATION
        if "widget" not in kwargs:
            kwargs["widget"] = SemanticSelectMultiple()
        # END CUSTOMIZATION

        form_field = db_field.formfield(**kwargs)

        # BEGIN CUSTOMIZATION
        # if isinstance(form_field.widget, SemanticSelectMultiple) and not isinstance(
        #     form_field.widget,
        #     (SemanticCheckboxSelectMultiple, SemanticAutocompleteSelectMultiple),
        # ):
        #     msg = _(
        #         "Hold down “Control”, or “Command” on a Mac, to select more than one."
        #     )
        #     help_text = form_field.help_text
        #     form_field.help_text = (
        #         format_lazy("{} {}", help_text, msg) if help_text else msg
        #     )
        # END CUSTOMIZATION

        return form_field

    def get_changelist_form(self, request, **kwargs):
        """
        Return a Form class for use in the Formset on the changelist page.
        """
        # BEGIN CUSTOMIZATION
        defaults = {
            "formfield_callback": partial(
                # Override formfield_callback so checkboxes render correctly
                self.changelist_formfield_for_dbfield,
                request=request,
            ),
            **kwargs,
        }
        # END CUSTOMIZATION
        if defaults.get("fields") is None and not modelform_defines_fields(
            defaults.get("form")
        ):
            defaults["fields"] = forms.ALL_FIELDS
        return modelform_factory(self.model, **defaults)

    def get_changelist_formset(self, request, **kwargs):
        """
        Return a FormSet class for use on the changelist page if list_editable
        is used.
        """
        # BEGIN CUSTOMIZATION
        defaults = {
            # Override formfield_callback so checkboxes render correctly
            "formfield_callback": partial(
                self.changelist_formfield_for_dbfield, request=request
            ),
            **kwargs,
        }
        # END CUSTOMIZATION
        return modelformset_factory(
            self.model,
            self.get_changelist_form(request),
            extra=0,
            fields=self.list_editable,
            **defaults
        )

    def changelist_formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if formfield and isinstance(formfield.widget, SemanticCheckboxInput):
            formfield.widget = SemanticChangelistCheckboxInput()
        return formfield

    def get_exclude(self, request, obj=None):
        # TODO: Verify and delete this method
        """
        Hook for specifying exclude.
        """
        return self.exclude


class SemanticModelAdmin(SemanticBaseModelAdmin, AwesomeSearchModelAdmin):
    action_form = SemanticActionForm

    def action_checkbox(self, obj):
        """
        A list_display column containing a checkbox widget.
        """
        semantic_checkbox = SemanticActionCheckboxInput(
            {"class": "action-select"}, lambda value: False
        )
        return semantic_checkbox.render(helpers.ACTION_CHECKBOX_NAME, str(obj.pk))

    action_checkbox.short_description = format_html(  # type: ignore
        format_html(
            """
            <div id="action-toggle" class="ui checkbox">
                <label></label><input id="action-toggle-input" type="checkbox">
            </div>
            """
        )
    )

    def autocomplete_view(self, request):
        return SemanticAutocompleteJsonView.as_view(model_admin=self)(request)


class SemanticStackedInline(SemanticBaseModelAdmin, StackedInline):
    pass


class SemanticTabularInline(SemanticBaseModelAdmin, TabularInline):
    pass
