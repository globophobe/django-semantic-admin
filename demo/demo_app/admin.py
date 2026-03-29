from django.conf import settings
from django.contrib import admin
from django.contrib.admin import ModelAdmin as DefaultModelAdmin
from django.contrib.admin import StackedInline as DefaultStackedInline
from django.contrib.admin import TabularInline as DefaultTabularInline
from django.contrib.auth.models import Group, User
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _
from taggit.models import Tag

from semantic_admin import (
    SemanticModelAdmin,
    SemanticStackedInline,
    SemanticTabularInline,
)

from .filters import PersonFilter
from .models import Favorite, Person, Picture


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Tag)

if "semantic_admin" in settings.INSTALLED_APPS:
    ModelAdmin = SemanticModelAdmin
    StackedInline = SemanticStackedInline
    TabularInline = SemanticTabularInline
else:
    ModelAdmin = DefaultModelAdmin
    StackedInline = DefaultStackedInline
    TabularInline = DefaultTabularInline


def html5_picture(obj: Picture, css: str = "") -> str:
    """HTML5 picture."""
    name = str(obj)
    return format_html("{}<em>{}</em>", obj.get_img(css=css), name)


class PictureStackedInline(StackedInline):
    """Picture stacked inline."""

    model = Picture
    fields = (
        ("date_and_time", "tags"),
        "inline_picture",
        "is_color",
    )
    readonly_fields = ("inline_picture",)
    show_change_link = True
    extra = 0

    @admin.display(
        description=_("picture").capitalize()
    )
    def inline_picture(self, obj: Picture) -> str:
        """Inline picture."""
        return html5_picture(obj, css="large rounded")


    def has_add_permission(self, *args, **kwargs) -> bool:
        """Has add permission."""
        return False


class PersonFavoriteTabularInline(TabularInline):
    """Person favorite tabular inline."""

    model = Favorite
    autocomplete_fields = fields = ("picture",)
    extra = 0


@admin.register(Person)
class PersonAdmin(ModelAdmin):
    """Person admin."""

    search_fields = ("name",)
    filterset_class = PersonFilter
    list_display = ("name", "birthday", "list_friends", "list_favorites")
    list_editable = ("birthday",)
    fieldsets = (
        (None, {"fields": (("name", "birthday"),)}),
        (_("extra").capitalize(), {"fields": (("slug", "url", "email"),)}),
        (None, {"fields": ("friends",)}),
    )
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("friends",)
    list_per_page = 10
    actions = ("send_friend_request",)
    inlines = (PictureStackedInline, PersonFavoriteTabularInline)

    @admin.display(
        description=_("friends").capitalize()
    )
    def list_friends(self, obj: Person) -> str:
        """List friends."""
        return format_html_join(
            ", ",
            '<a href="{}">{}</a>',
            (
                (reverse("admin:demo_app_person_change", args=(friend.pk,)), friend.name)
                for friend in obj.friends.all()
            ),
        )


    @admin.display(
        description=_("favorites").capitalize()
    )
    def list_favorites(self, obj: Person) -> str:
        """List favorites."""
        return format_html_join(
            "",
            '<a href="{}">{}<em>{}</em></a>',
            (
                (
                    reverse("admin:demo_app_picture_change", args=(favorite.picture.pk,)),
                    favorite.picture.get_img(css="tiny rounded"),
                    str(favorite.picture),
                )
                for favorite in obj.favorites.all()
            ),
        )


    def send_friend_request(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Send friend request."""
        msg = _("You are now friends with {friends}.")
        format_dict = {"friends": ", ".join(obj.name for obj in queryset)}
        self.message_user(request, msg.format(**format_dict))

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Get queryset."""
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("friends", "favorites__picture")


class PictureFavoriteTabularInline(TabularInline):
    """Picture favorite tabular inline."""

    model = Favorite
    autocomplete_fields = fields = ("person",)
    extra = 0


@admin.register(Picture)
class PictureAdmin(ModelAdmin):
    """Picture admin."""

    search_fields = ("tags__name",)
    list_filter = ("person",)
    list_display = (
        "list_picture",
        "person",
        "date_and_time",
        "is_color",
        "has_favorites",
    )
    list_editable = (
        "person",
        "date_and_time",
        "is_color",
    )
    fields = (
        ("date_and_time", "tags", "is_color"),
        "detail_picture",
    )
    readonly_fields = (
        "list_picture",
        "person_changelink",
        "has_favorites",
        "detail_picture",
    )
    date_hierarchy = "date_and_time"
    list_per_page = 10
    inlines = (PictureFavoriteTabularInline,)

    @admin.display(
        description=_("picture").capitalize(),
        ordering="date_and_time",
    )
    def list_picture(self, obj: Picture) -> str:
        """List picture."""
        return html5_picture(obj, css="medium rounded")


    @admin.display(
        description=_("picture").capitalize()
    )
    def detail_picture(self, obj: Picture) -> str:
        """Detail picture."""
        return html5_picture(obj, css="large rounded")


    @admin.display(
        description=_("person").capitalize(),
        ordering="person",
    )
    def person_changelink(self, obj: Picture) -> str:
        """Person change link."""
        url = reverse("admin:demo_app_person_change", args=(obj.person_id,))
        return format_html('<a href="{}">{}</a>', url, obj.person.name)


    @admin.display(
        description=_("has favorites").capitalize(),
        boolean=True,
        ordering="total_favorites",
    )
    def has_favorites(self, obj: Picture) -> bool:
        """Has favorites."""
        return obj.total_favorites > 1


    def has_add_permission(self, *args, **kwargs) -> bool:
        """Has add permission."""
        return False

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        """Get queryset."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("person")
        queryset = queryset.prefetch_related("tags")
        return queryset.annotate(total_favorites=Count("favorites"))
