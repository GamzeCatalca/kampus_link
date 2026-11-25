
from django.contrib import admin
from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "event",
        "status",
        "registered_at",
    )

    list_filter = (
        "status",
        "registered_at",
    )

    search_fields = (
        "student__username",
        "student__email",
        "event__title",
    )

    readonly_fields = (
        "registered_at",
    )
