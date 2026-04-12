from django.contrib import admin

from semantic_admin import SemanticModelAdmin, SemanticTabularInline

from .filters import EventFilter
from .models import Category, Event, EventNote


class EventNoteInline(SemanticTabularInline):
    model = EventNote
    fields = ("label",)
    extra = 0


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

