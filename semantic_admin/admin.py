from django import forms
from django.contrib.admin import helpers, widgets
from django.contrib.admin.options import (
    BaseModelAdmin,
    StackedInline,
    TabularInline,
    get_ul_class,
)
from django.forms.widgets import CheckboxSelectMultiple, SelectMultiple
from django.utils.html import mark_safe
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _

from .awesomesearch import AwesomeSearchModelAdmin
from .views.autocomplete import SemanticAutocompleteJsonView
from .widgets import SemanticAutocompleteSelect, SemanticAutocompleteSelectMultiple


class SemanticCheckboxInput(forms.CheckboxInput):
    template_name = "django/forms/widgets/changelist_checkbox.html"


class SemanticAutocompleteBase(BaseModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Get a form Field for a ForeignKey.
        """
        db = kwargs.get("using")

        if db_field.name in self.get_autocomplete_fields(request):

            # BEGIN CUSTOMIZATION
            kwargs["widget"] = SemanticAutocompleteSelect(
                db_field.remote_field, self.admin_site, using=db
            )
            # END CUSTOMIZATION

        elif db_field.name in self.raw_id_fields:
            kwargs["widget"] = widgets.ForeignKeyRawIdWidget(
                db_field.remote_field, self.admin_site, using=db
            )
        elif db_field.name in self.radio_fields:
            kwargs["widget"] = widgets.AdminRadioSelect(
                attrs={"class": get_ul_class(self.radio_fields[db_field.name])}
            )
            kwargs["empty_label"] = _("None") if db_field.blank else None

        if "queryset" not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs["queryset"] = queryset

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

        autocomplete_fields = self.get_autocomplete_fields(request)
        if db_field.name in autocomplete_fields:

            # BEGIN CUSTOMIZATION
            kwargs["widget"] = SemanticAutocompleteSelectMultiple(
                db_field.remote_field, self.admin_site, using=db
            )
            # END CUSTOMIZATION

        elif db_field.name in self.raw_id_fields:
            kwargs["widget"] = widgets.ManyToManyRawIdWidget(
                db_field.remote_field, self.admin_site, using=db
            )
        elif db_field.name in list(self.filter_vertical) + list(self.filter_horizontal):
            kwargs["widget"] = widgets.FilteredSelectMultiple(
                db_field.verbose_name, db_field.name in self.filter_vertical
            )

        if "queryset" not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs["queryset"] = queryset

        form_field = db_field.formfield(**kwargs)

        # BEGIN CUSTOMIZATION
        if isinstance(form_field.widget, SelectMultiple) and not isinstance(
            form_field.widget,
            (CheckboxSelectMultiple, SemanticAutocompleteSelectMultiple),
        ):
            msg = _(
                'Hold down "Control", or "Command" on a Mac, to select more than one.'
            )
            # END CUSTOMIZATION
            help_text = form_field.help_text
            form_field.help_text = (
                format_lazy("{} {}", help_text, msg) if help_text else msg
            )
        return form_field


class SemanticModelAdmin(SemanticAutocompleteBase, AwesomeSearchModelAdmin):
    def action_checkbox(self, obj):
        """
        A list_display column containing a checkbox widget.
        """
        semantic_checkbox = SemanticCheckboxInput(
            {"class": "action-select"}, lambda value: False
        )
        return semantic_checkbox.render(helpers.ACTION_CHECKBOX_NAME, str(obj.pk))

    action_checkbox.short_description = mark_safe(
        '<div id="action-toggle" class="ui checkbox"><label></label><input type="checkbox" ></div>'
    )

    def autocomplete_view(self, request):
        return SemanticAutocompleteJsonView.as_view(model_admin=self)(request)


class SemanticStackedInline(SemanticAutocompleteBase, StackedInline):
    pass


class SemanticTabularInline(SemanticAutocompleteBase, TabularInline):
    pass
