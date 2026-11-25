from django.contrib import admin
from .models import University


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "website",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "description",
    )

    readonly_fields = (
        "created_at",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }