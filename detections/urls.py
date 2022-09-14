from django.urls import path
from detections import views

app_name = "detections"
urlpatterns = [
    path("", views.CariesDetectionView.as_view(), name="detect"),
]
