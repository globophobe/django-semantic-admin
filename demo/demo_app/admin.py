from django.conf import settings
from django.contrib import admin
from django.contrib.admin import ModelAdmin as DefaultModelAdmin
from django.contrib.admin import StackedInline as DefaultStackedInline
from django.contrib.admin import TabularInline as DefaultTabularInline
from django.contrib.auth.models import Group, User
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from semantic_admin import (
    SemanticModelAdmin,
    SemanticStackedInline,
    SemanticTabularInline,
)
from taggit.models import Tag

from .filters import PersonFilter
from .models import Favorite, Person, Picture

try:
    from django.utils.translation import gettext_lazy as _  # Django >= 4
except ImportError:
    from django.utils.translation import ugettext_lazy as _


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


def html5_picture(obj, css=""):
    name = str(obj)
    img = obj.get_img(css=css)
    html = f"{img}<em>{name}</em>"
    return format_html(mark_safe(html))


class PictureStackedInline(StackedInline):
    model = Picture
    fields = (
        ("date_and_time", "tags"),
        "inline_picture",
        "is_color",
    )
    readonly_fields = ("inline_picture",)
    show_change_link = True
    extra = 0

    def inline_picture(self, obj):
        return html5_picture(obj, css="large rounded")

    inline_picture.short_description = _("picture").capitalize()  # type: ignore

    def has_add_permission(self, request, obj=None):
        return False


class PersonFavoriteTabularInline(TabularInline):
    model = Favorite
    autocomplete_fields = fields = ("picture",)
    extra = 0


@admin.register(Person)
class PersonAdmin(ModelAdmin):
    search_fields = ("name",)
    filter_class = PersonFilter
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

    def list_friends(self, obj):
        friends = []
        for friend in obj.friends.all():
            url = reverse("admin:demo_app_person_change", args=(friend.pk,))
            a = f"<a href={url}>{friend.name}</a>"
            friends.append(a)
        html = ", ".join(friends)
        return format_html(mark_safe(html))

    list_friends.short_description = _("friends").capitalize()  # type: ignore

    def list_favorites(self, obj):
        favorites = []
        for favorite in obj.favorites.all():
            picture = favorite.picture
            name = str(picture)
            url = reverse("admin:demo_app_picture_change", args=(picture.pk,))
            img = picture.get_img(css="tiny rounded")
            a = f"<a href={url}>{img}<em>{name}</em></a>"
            favorites.append(a)
        html = "".join(favorites)
        return format_html(mark_safe(html))

    list_favorites.short_description = _("favorites").capitalize()  # type: ignore

    def send_friend_request(self, request, queryset):
        msg = _("You are now friends with {friends}.")
        format_dict = {"friends": ", ".join((obj.name for obj in queryset))}
        self.message_user(request, msg.format(**format_dict))

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related("friends", "favorites__picture")


class PictureFavoriteTabularInline(TabularInline):
    model = Favorite
    autocomplete_fields = fields = ("person",)
    extra = 0


@admin.register(Picture)
class PictureAdmin(ModelAdmin):
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

    def list_picture(self, obj):
        return html5_picture(obj, css="medium rounded")

    list_picture.short_description = _("picture").capitalize()  # type: ignore
    list_picture.admin_order_field = "date_and_time"  # type: ignore

    def detail_picture(self, obj):
        return html5_picture(obj, css="large rounded")

    detail_picture.short_description = _("picture").capitalize()  # type: ignore

    def person_changelink(self, obj):
        url = reverse("admin:demo_app_person_change", args=(obj.pk,))
        a = f"<a href={url}>{obj.person.name}</a>"
        return format_html(mark_safe(a))

    person_changelink.short_description = _("person").capitalize()  # type: ignore
    person_changelink.admin_order_field = "person"  # type: ignore

    def has_favorites(self, obj):
        return obj.total_favorites > 1

    has_favorites.short_description = _("has favorites").capitalize()  # type: ignore
    has_favorites.admin_order_field = "total_favorites"
    has_favorites.boolean = True  # type: ignore

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("person")
        queryset = queryset.prefetch_related("tags")
        return queryset.annotate(total_favorites=Count("favorites"))
