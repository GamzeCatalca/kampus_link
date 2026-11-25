from django.urls import path

from .views import (
    ClubListView,
    ClubDetailView,
    ClubCreateView,
    MyClubApplicationsView,
)


urlpatterns = [
    path("", ClubListView.as_view(), name="club-list"),
    path("create/", ClubCreateView.as_view(), name="club-create"),
    path("my/", MyClubApplicationsView.as_view(), name="my-club-applications"),
    path("<int:pk>/", ClubDetailView.as_view(), name="club-detail"),
]