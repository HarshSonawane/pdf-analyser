from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from core.models import ReviewRequest, PageResult


class ReviewRequestSerializer(serializers.ModelSerializer):
    document_name = serializers.SerializerMethodField()

    class Meta:
        model = ReviewRequest
        fields = ["id", "document", "reviewer", "document_name", "output", "status", "created_at"]

    def get_document_name(self, obj):
        return obj.document.name.split("/")[-1]


class PageResultSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()

    class Meta:
        model = PageResult
        fields = [
            "id",
            "review_request",
            "page_number",
            "flaged",
            "service",
            "details",
            "created_at",
        ]
        read_only_fields = ["created_at"]


    def get_details(self, obj):
        errors = {}
        # obj.details is dict
        # only get is_blank and inside_borders
        if obj.details.get("is_blank"):
            errors["is_blank"] = _("Page is blank")

        if not obj.details.get("inside_borders"):
            errors["margins_not_followed"] = _("Data is outside the borders")

        return errors
