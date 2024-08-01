from django.urls import path, include

urlpatterns = [
    path("", include("core.v1.urls")),
    path("", include("users.v1.urls")),
]
