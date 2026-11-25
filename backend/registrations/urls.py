from django.urls import path
from .views import (
    RegistrationCreateView,
    RegistrationCancelView,
    MyRegistrationsView,
)


urlpatterns = [
    path(
        "",
        RegistrationCreateView.as_view(),
        name="registration-create",
    ),
    path(
        "my/",
        MyRegistrationsView.as_view(),
        name="my-registrations",
    ),
    path(
        "<int:pk>/cancel/",
        RegistrationCancelView.as_view(),
        name="registration-cancel",
    ),
]