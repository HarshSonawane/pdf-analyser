from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User

from app.utils.permissions import HasAPIkey
from users.v1.serializers import (
    RegisterSerializer,
    UserAuthSerializer,
    UserDetailsSerializer,
)


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password1", "password2")
)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [
        HasAPIkey,
    ]

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            UserAuthSerializer(user, context=self.token).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        user = serializer.save()
        self.token = get_tokens_for_user(user)
        return user


class Users(generics.ListCreateAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = (
        HasAPIkey,
        permissions.IsAuthenticated,
    )
    authentication_classes = (
        TokenAuthentication,
        JWTAuthentication,
    )

    def get_queryset(self):
        queryset = User.objects.order_by("-date_joined")

        role = self.request.query_params.get("role", None)
        if role:
            if "-" in role:
                queryset = queryset.filter(role__id=role)
            else:
                queryset = queryset.filter(role__slug=role)

        is_active = self.request.query_params.get("is_active", None)
        if is_active:
            queryset = queryset.filter(is_active=bool(int(is_active)))

        q = self.request.query_params.get("q", None)
        if q:
            queryset = queryset.annotate(
                name=Concat(
                    "first_name",
                    V(" "),
                    "last_name",
                ),
            ).filter(
              Q(phone__icontains=q)
              | Q(name__icontains=q)
              | Q(first_name__icontains=q)
              | Q(last_name__icontains=q)
            )
            return queryset
        return queryset

    def get (self, request, *args, **kwargs):
        queryset = self.get_queryset()
        active_users = queryset.filter(is_active=True).count()
        inactive_users = queryset.filter(is_active=False).count()
        response = super().get(request, *args, **kwargs)
        response.data["active_users"] = active_users
        response.data["inactive_users"] = inactive_users
        return response


class UserDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = (
        HasAPIkey,
        permissions.IsAuthenticated,
    )
    authentication_classes = (
        TokenAuthentication,
        JWTAuthentication,
    )

    def get_object(self):
        try:
            return User.objects.get(pk=self.kwargs.get("pk"))
        except ObjectDoesNotExist:
            raise Http404("User does not exists")

    def patch(self, request, *args, **kwargs):
        self.serializer_class = UserDetailsSerializer
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(
            data={"detail": "User has been deactivated successfully"},
            status=status.HTTP_200_OK,
        )


class AuthenticatedUser(generics.RetrieveAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = (
        HasAPIkey,
        permissions.IsAuthenticated,
    )
    authentication_classes = (
        TokenAuthentication,
        JWTAuthentication,
    )

    def get_object(self):
        return self.request.user


class HealthCheck(generics.GenericAPIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        result = {"status": "ok", "message": "Server is running", "code": 200, "data": []}
        return Response(result, status=status.HTTP_200_OK)
