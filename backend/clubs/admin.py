
from django.contrib import admin, messages

from .models import Club


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "university",
        "representative",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "university",
    )

    search_fields = (
        "name",
        "description",
        "university__name",
        "representative__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    autocomplete_fields = (
        "representative",
    )

    actions = (
        "approve_clubs",
        "reject_clubs",
    )

    @admin.action(description="Approve selected club applications")
    def approve_clubs(self, request, queryset):

        approved_count = 0
        skipped_count = 0

        for club in queryset:

            if club.status != Club.Status.PENDING:
                skipped_count += 1
                continue

            if not club.representative:
                skipped_count += 1
                continue

            club.status = Club.Status.APPROVED
            club.save(update_fields=["status", "updated_at"])

            representative = club.representative

            if representative.role != "ADMIN":
                representative.role = "CLUB_REP"
                representative.save(update_fields=["role"])

            approved_count += 1

        self.message_user(
            request,
            f"{approved_count} club application(s) approved. "
            f"{skipped_count} skipped.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Reject selected club applications")
    def reject_clubs(self, request, queryset):

        rejected_count = 0
        skipped_count = 0

        for club in queryset:

            if club.status != Club.Status.PENDING:
                skipped_count += 1
                continue

            club.status = Club.Status.REJECTED
            club.save(update_fields=["status", "updated_at"])

            representative = club.representative

            if representative and representative.role == "CLUB_REP":

                other_approved_clubs = (
                    representative.represented_clubs
                    .filter(status=Club.Status.APPROVED)
                    .exclude(pk=club.pk)
                    .exists()
                )

                if not other_approved_clubs:
                    representative.role = "STUDENT"
                    representative.save(update_fields=["role"])

            rejected_count += 1

        self.message_user(
            request,
            f"{rejected_count} club application(s) rejected. "
            f"{skipped_count} skipped.",
            level=messages.SUCCESS,
        )

    def save_model(self, request, obj, form, change):

        if change and obj.pk:
            old_club = Club.objects.get(pk=obj.pk)
            was_pending = old_club.status == Club.Status.PENDING
        else:
            was_pending = False

        super().save_model(request, obj, form, change)

        if (
            was_pending
            and obj.status == Club.Status.APPROVED
            and obj.representative
        ):
            representative = obj.representative

            if representative.role != "ADMIN":
                representative.role = "CLUB_REP"
                representative.save(update_fields=["role"])

        elif (
            was_pending
            and obj.status == Club.Status.REJECTED
            and obj.representative
            and obj.representative.role == "CLUB_REP"
        ):
            representative = obj.representative

            other_approved_clubs = (
                representative.represented_clubs
                .filter(status=Club.Status.APPROVED)
                .exclude(pk=obj.pk)
                .exists()
            )

            if not other_approved_clubs:
                representative.role = "STUDENT"
                representative.save(update_fields=["role"])
