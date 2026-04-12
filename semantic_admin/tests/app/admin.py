from django.contrib import admin

from semantic_admin import SemanticModelAdmin, SemanticTabularInline

from .filters import EventFilter
from .models import Category, Event, EventNote


class EventNoteInline(SemanticTabularInline):
    model = EventNote
    fields = ("label",)
    extra = 0

    def has_add_permission(self, request, obj=None) -> bool:
        """Disallow adding inline rows."""
        return False


@admin.register(Category)
class CategoryAdmin(SemanticModelAdmin):
    list_display = ("name",)


@admin.register(Event)
class EventAdmin(SemanticModelAdmin):
    filterset_class = EventFilter
    search_fields = ("name",)
    list_display = ("name", "category", "when", "is_active")
    list_editable = ("category", "when", "is_active")
    inlines = (EventNoteInline,)
