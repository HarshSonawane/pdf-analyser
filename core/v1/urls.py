from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.v1.views import (
  ReviewRequestListCreateView,
  ReviewRequestRetrieveUpdateDestroyView,
  PageResultListCreateView,
  PageResultRetrieveUpdateDestroyView
)

urlpatterns = [
    path("review-requests/", ReviewRequestListCreateView.as_view(), name="review-requests"),
    path("review-requests/<uuid:pk>/", ReviewRequestRetrieveUpdateDestroyView.as_view(), name="review-request"),
    path("review-requests/<uuid:review_requests_pk>/results/", PageResultListCreateView.as_view(), name="results"),
    path("page-results/", PageResultListCreateView.as_view(), name="page-results"),
    path("page-results/<uuid:pk>/", PageResultRetrieveUpdateDestroyView.as_view(), name="page-result"),
]
