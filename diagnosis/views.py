from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveAPIView,
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from diagnosis.filters import DentalDiagnosisFilter
from diagnosis.serializers import DentalDiagnosisSerializer

from .models import DentalDiagnosis


class DentalDiagnosisUserInformationView(RetrieveAPIView):
    """
    get: Retrieve user's DentalDiagnosis information.
    """

    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user_diagnosis = DentalDiagnosis.objects.filter(user=self.request.user.id)
        last_diagnosis = (
            user_diagnosis.latest("date_created") if user_diagnosis else None
        )
        total_diagnosis = user_diagnosis.count() if user_diagnosis else 0
        data = {
            "last_diagnosis": last_diagnosis.date_created if last_diagnosis else None,
            "total_diagnosis": total_diagnosis,
        }
        return Response(data, status=status.HTTP_201_CREATED)


class DentalDiagnosisView(ListCreateAPIView):
    """
    get: List all user's DentalDiagnosis.
    post: Creates new DentalDiagnosis.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DentalDiagnosisSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DentalDiagnosisFilter
    pagination_class = LimitOffsetPagination

    def create(self, request, *args, **kwargs):
        """
        Register a new dental diagnosis.
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            dental_diagnosis: DentalDiagnosis = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        return DentalDiagnosis.objects.filter(user=self.request.user.id)


class DentalDiagnosisDetailView(RetrieveUpdateDestroyAPIView):
    """
    get: Retrieves a user's DentalDiagnosis by Id
    put: Updates a user's DentalDiagnosis by Id
    delete: Deletes a user's DentalDiagnosis by Id
    """

    http_method_names = ["get", "delete", "put"]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DentalDiagnosisSerializer
    lookup_field = "id"

    def get_queryset(self):
        return DentalDiagnosis.objects.filter(user=self.request.user.id)
