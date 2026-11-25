from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "club",
        "start_datetime",
        "status",
        "capacity",
        "created_by",
    )

    list_filter = (
        "status",
        "club",
        "start_datetime",
    )

    search_fields = (
        "title",
        "description",
        "location",
        "club__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }