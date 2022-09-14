from rest_framework import serializers
from rest_framework.serializers import Serializer

__all__ = [
    "CariesDetectionSerializer",
]


class CariesDetectionSerializer(Serializer):
    denture_images = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
    )

    # def validate(self, data):
    #     denture_images = data.get("denture_images")
    #     errors = dict()

    #     if errors:
    #         raise ValidationError(errors)

    #     return super(DentalDiagnosisSerializer, self).validate(data)
