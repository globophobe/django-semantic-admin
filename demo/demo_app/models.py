import os

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager


class Person(models.Model):
    friends = models.ManyToManyField(
        "self", related_name="friends_with", help_text="Helpful text"
    )
    name = models.CharField(_("name"), max_length=256, help_text="Helpful text")
    slug = models.SlugField(_("slug"), help_text="Helpful text")
    url = models.URLField(_("url"), help_text="Helpful text")
    email = models.EmailField(_("email"), help_text="Helpful text")
    birthday = models.DateField(_("birthday"), help_text="Helpful text")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("person")
        verbose_name_plural = _("people")


class Picture(models.Model):
    person = models.ForeignKey(
        "Person",
        related_name="pictures",
        on_delete=models.CASCADE,
        help_text="Helpful text",
    )
    date_and_time = models.DateTimeField(
        _("date and time"),
        help_text="Helpful text",
    )
    picture = models.ImageField(
        _("picture"), help_text="Helpful text", upload_to="pictures"
    )
    is_color = models.BooleanField(_("color"), help_text="Helpful text", default=True)
    tags = TaggableManager()

    @property
    def admin_url(self):
        return reverse("admin:demo_app_picture_change", args=(self.pk,))

    @property
    def url(self):
        if self.picture and os.path.exists(self.picture.path):
            filename = self.picture.name
            self.picture.close()
            return settings.MEDIA_URL + filename

    def get_img(self, css="", style=""):
        return f'<img class="ui {css} image" style="{style}" src={self.url} />'

    @property
    def semantic_autocomplete(self):
        name = str(self)
        img = self.get_img(css="small rounded right spaced")
        html = f"<p>{img}{name}</p>"
        return format_html(mark_safe(html))

    def __str__(self):
        return ", ".join((tag.name for tag in self.tags.all()))

    class Meta:
        ordering = ("-date_and_time",)
        verbose_name = _("picture")
        verbose_name_plural = _("pictures")


class Favorite(models.Model):
    person = models.ForeignKey(
        "Person",
        related_name="favorites",
        on_delete=models.CASCADE,
        help_text="Helpful text",
    )
    picture = models.ForeignKey(
        "Picture",
        related_name="favorites",
        on_delete=models.CASCADE,
        help_text="Helpful text",
    )

    def __str__(self):
        return format_html('<i class="large red heart icon"></i>')

    class Meta:
        verbose_name = _("favorite")
        verbose_name_plural = _("favorites")
