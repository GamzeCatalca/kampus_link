
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import University
from .serializers import UniversitySerializer


class UniversityListView(generics.ListAPIView):
    serializer_class = UniversitySerializer
    permission_classes = [AllowAny]

    queryset = (
        University.objects
        .filter(is_active=True)
        .order_by("name")
    )


class UniversityDetailView(generics.RetrieveAPIView):
    serializer_class = UniversitySerializer
    permission_classes = [AllowAny]

    queryset = University.objects.filter(is_active=True)
