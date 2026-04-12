from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.name


class Event(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="events",
    )
    name = models.CharField(max_length=128)
    when = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class EventNote(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    label = models.CharField(max_length=128)

    def __str__(self) -> str:
        return self.label

