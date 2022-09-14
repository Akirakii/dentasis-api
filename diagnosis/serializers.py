from accounts.models import User
from django.contrib.auth import authenticate, password_validation
from django.core import exceptions
from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer, ValidationError

from diagnosis.models import DentalDiagnosis, DentalDiagnosisDentureImage

__all__ = [
    "DentalDiagnosisSerializer",
]


class DentalDiagnosisDentureImageSerializer(ModelSerializer):
    class Meta:
        model = DentalDiagnosisDentureImage
        exclude = ["dental_diagnosis"]


class DentalDiagnosisSerializer(ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    denture_images = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True,
        required=False,
    )
    dental_diagnosis_denture_images = DentalDiagnosisDentureImageSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = DentalDiagnosis
        fields = "__all__"
        extra_kwargs = {
            "danger_percentage": {"required": False},
        }

    def validate(self, data):
        denture_images = data.get("denture_images")
        danger_percentage = data.get("danger_percentage")
        errors = dict()

        if self.context["request"].method == "POST":
            if denture_images is None:
                errors.setdefault("denture_images", []).append(
                    "This field is required."
                )
            if danger_percentage is None:
                errors.setdefault("danger_percentage", []).append(
                    "This field is required."
                )

        if errors:
            raise ValidationError(errors)

        return super(DentalDiagnosisSerializer, self).validate(data)

    @transaction.atomic
    def create(self, validated_data):
        formatted_data = {
            "user": validated_data.get("user"),
            "is_favorite": validated_data.get("is_favorite"),
            "danger_percentage": validated_data.get("danger_percentage"),
            "name": validated_data.get("name"),
            "description": validated_data.get("description"),
        }

        dental_diagnosis = DentalDiagnosis(**formatted_data)
        dental_diagnosis.save()

        for image in validated_data.get("denture_images"):
            DentalDiagnosisDentureImage(
                image_url=image, dental_diagnosis=dental_diagnosis
            ).save()

        return dental_diagnosis

    def update(self, instance, validated_data):
        instance.is_favorite = validated_data.get("is_favorite", instance.is_favorite)
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.save()
        return instance
