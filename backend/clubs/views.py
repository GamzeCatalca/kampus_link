
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Club
from .serializers import ClubSerializer, ClubCreateSerializer


class ClubListView(generics.ListAPIView):
    serializer_class = ClubSerializer
    permission_classes = [AllowAny]

    queryset = (
        Club.objects
        .filter(status=Club.Status.APPROVED)
        .select_related("university")
        .order_by("name")
    )


class ClubDetailView(generics.RetrieveAPIView):
    serializer_class = ClubSerializer
    permission_classes = [AllowAny]

    queryset = (
        Club.objects
        .filter(status=Club.Status.APPROVED)
        .select_related("university")
    )


class ClubCreateView(generics.CreateAPIView):
    serializer_class = ClubCreateSerializer
    permission_classes = [IsAuthenticated]
class MyClubApplicationsView(generics.ListAPIView):
    serializer_class = ClubSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Club.objects
            .filter(representative=self.request.user)
            .select_related("university")
            .order_by("-created_at")
        )
