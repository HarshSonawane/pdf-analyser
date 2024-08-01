from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from core.models import ReviewRequest, PageResult


class ReviewRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewRequest
        fields = ['id', 'document', 'reviewer', 'status', 'created_at']


class PageResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageResult
        fields = ['id', 'review_request', 'page_number', 'service', 'details', 'created_at']
        read_only_fields = ['created_at']
