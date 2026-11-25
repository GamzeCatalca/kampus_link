
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from .models import Event
from .serializers import EventSerializer, EventCreateSerializer
from .permissions import CanCreateEvent, CanManageEvent


class EventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "title",
        "description",
        "location",
        "club__name",
    ]
    ordering_fields = [
        "start_datetime",
        "title",
    ]
    ordering = ["start_datetime"]
    pagination_class = EventPagination

    def get_queryset(self):
        queryset = (
            Event.objects
            .filter(status=Event.Status.PUBLISHED)
            .select_related("club", "club__university")
        )

        university_id = self.request.query_params.get("university")
        club_id = self.request.query_params.get("club")

        if university_id:
            queryset = queryset.filter(
                club__university_id=university_id
            )

        if club_id:
            queryset = queryset.filter(club_id=club_id)

        return queryset


class EventDetailView(generics.RetrieveAPIView):
    serializer_class = EventSerializer
    permission_classes = [AllowAny]

    queryset = (
        Event.objects
        .filter(status=Event.Status.PUBLISHED)
        .select_related("club", "club__university")
    )


class EventCreateView(generics.CreateAPIView):
    serializer_class = EventCreateSerializer
    permission_classes = [CanCreateEvent]


class EventUpdateView(generics.UpdateAPIView):
    serializer_class = EventCreateSerializer
    permission_classes = [CanManageEvent]

    queryset = Event.objects.select_related("club")


class EventDeleteView(generics.DestroyAPIView):
    permission_classes = [CanManageEvent]
    serializer_class = EventSerializer
    queryset = Event.objects.select_related("club")
