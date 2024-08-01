from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.v1.views import (
  RegisterView,
  UserDetails,
  Users,
  AuthenticatedUser,
  HealthCheck,
)

urlpatterns = [
    path('healthcheck/', HealthCheck.as_view(), name='healthcheck'),
    path("users/", Users.as_view(), name="users"),
    path("users/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/me/", AuthenticatedUser.as_view(), name="user"),
    path("users/logout/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/register/", RegisterView.as_view(), name="register"),
    path("users/<uuid:pk>/", UserDetails.as_view(), name="user"),
]
