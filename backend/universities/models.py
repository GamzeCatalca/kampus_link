from django.db import models
from django.utils.text import slugify


class University(models.Model):

    name = models.CharField(
        max_length=150,
        unique=True,
    )

    slug = models.SlugField(
        max_length=170,
        unique=True,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    website = models.URLField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "University"
        verbose_name_plural = "Universities"
        ordering = ["name"]