from django.conf import settings
from django.db import models
from django.utils.text import slugify

from universities.models import University


class Club(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name="clubs",
    )

    name = models.CharField(
        max_length=150,
    )

    slug = models.SlugField(
        max_length=170,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    logo_url = models.URLField(
        blank=True,
    )

    representative = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="represented_clubs",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.university.name}"

    class Meta:
        verbose_name = "Club"
        verbose_name_plural = "Clubs"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["university", "name"],
                name="unique_club_name_per_university",
            ),
            models.UniqueConstraint(
                fields=["university", "slug"],
                name="unique_club_slug_per_university",
            ),
        ]