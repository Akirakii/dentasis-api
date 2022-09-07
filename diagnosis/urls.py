from django.urls import path
from diagnosis import views

app_name = "diagnosis"
urlpatterns = [
    path("", views.DentalDiagnosisView.as_view(), name="diagnosis"),
    path(
        "<int:id>/",
        views.DentalDiagnosisDetailView.as_view(),
        name="diagnosis-detail",
    ),
]
