import django_filters
from django.db import models

from diagnosis.models import DentalDiagnosis

__all__ = [
    "DentalDiagnosisFilter",
]


class DentalDiagnosisFilter(django_filters.FilterSet):
    min_date = django_filters.IsoDateTimeFilter(
        field_name="date_created", lookup_expr="gte"
    )
    max_date = django_filters.IsoDateTimeFilter(
        field_name="date_created", lookup_expr="lte"
    )

    class Meta:
        model = DentalDiagnosis
        fields = ["name", "is_favorite"]
        filter_overrides = {
            models.CharField: {
                "filter_class": django_filters.CharFilter,
                "extra": lambda f: {
                    "lookup_expr": "icontains",
                },
            },
        }
