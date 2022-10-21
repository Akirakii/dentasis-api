from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()

__all__ = [
    "DentalDiagnosis",
    "DentalDiagnosisDentureImage",
]


class DentalDiagnosis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    is_favorite = models.BooleanField(default=False)
    danger_percentage = models.DecimalField(max_digits=3, decimal_places=2)
    name = models.CharField(max_length=25)
    description = models.CharField(max_length=255)

    class Meta:
        db_table = "diagnosis_dental_diagnosis"
        verbose_name = "diagnosis"
        verbose_name_plural = "diagnosis"


class DentalDiagnosisDentureImage(models.Model):
    dental_diagnosis = models.ForeignKey(
        DentalDiagnosis,
        on_delete=models.CASCADE,
        related_name="dental_diagnosis_denture_images",
    )
    image_url = models.CharField(max_length=255)

    class Meta:
        db_table = "diagnosis_dental_diagnosis_denture_image"
        verbose_name = "imagen"
        verbose_name_plural = "imagenes"
