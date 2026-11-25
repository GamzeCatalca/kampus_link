
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify

from clubs.models import Club


class Event(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="events",
    )

    title = models.CharField(max_length=200)

    slug = models.SlugField(
        max_length=220,
        blank=True,
    )

    description = models.TextField()

    location = models.CharField(max_length=255)

    start_datetime = models.DateTimeField()

    end_datetime = models.DateTimeField()

    registration_deadline = models.DateTimeField(
        null=True,
        blank=True,
    )

    capacity = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    cover_image_url = models.URLField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_events",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if (
            self.club_id
            and self.status == self.Status.PUBLISHED
            and self.club.status != Club.Status.APPROVED
        ):
            raise ValidationError({
                "club": "Only approved clubs can publish events."
            })

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["start_datetime"]
        constraints = [
            models.UniqueConstraint(
                fields=["club", "slug"],
                name="unique_event_slug_per_club",
            ),
        ]
