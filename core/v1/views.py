from django.core.exceptions import ObjectDoesNotExist

from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.db import IntegrityError

from django.http import Http404
from django.utils.decorators import method_decorator

from rest_framework import generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError


from core.models import ReviewRequest, PageResult

from .serializers import (
    ReviewRequestSerializer,
    PageResultSerializer,
)


class ReviewRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewRequestSerializer
    queryset = ReviewRequest.objects.all()
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class ReviewRequestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewRequestSerializer
    queryset = ReviewRequest.objects.all()
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return ReviewRequest.objects.get(
                Q(reviewer=self.request.user),
                pk=self.kwargs["pk"],
            )
        except ObjectDoesNotExist:
            raise Http404


class PageResultListCreateView(generics.ListCreateAPIView):
    serializer_class = PageResultSerializer
    queryset = PageResult.objects.all()
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
      review_requests_pk = self.kwargs.get("review_requests_pk")
      if review_requests_pk:
          return PageResult.objects.filter(review_request=review_requests_pk)
      return PageResult.objects.filter(review_request__reviewer=self.request.user)

    def perform_create(self, serializer):
        try:
            review_request = ReviewRequest.objects.get(
                Q(reviewer=self.request.user),
                pk=self.request.data["review_request"],
            )

        except ObjectDoesNotExist:
            raise ValidationError("Review request not found.")

        serializer.save(review_request=review_request)


class PageResultRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PageResultSerializer
    queryset = PageResult.objects.all()
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return PageResult.objects.get(
                review_request__reviewer=self.request.user,
                pk=self.kwargs["pk"],
            )
        except ObjectDoesNotExist:
            raise Http404