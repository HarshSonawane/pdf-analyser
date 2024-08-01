from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=150, min_length=5, required=True)
    email = serializers.EmailField(required=False)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                _("A user with that phone already exists.")
            )
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("A user with that email already exists.")
            )
        return value

    def validate(self, data):
        if data["password1"] != data["password2"]:
            raise serializers.ValidationError(
                _("The two password fields didn’t match.")
            )
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            phone=validated_data["phone"],
            email=validated_data["email"],
            password=validated_data["password1"],
        )

        return user

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class UserDetailsSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "status",
            "date_joined"
        )


    def get_status(self, obj):
      if obj.is_active:
        return "active"
      return "inactive"


class UserSerializer(serializers.ModelSerializer):
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "email",
            "first_name",
            "last_name",
            "updated_at",
        )

    def get_updated_at(self, obj):
        return obj.updated_at.strftime("%d-%m-%Y %H:%M:%S")


class UserAuthSerializer(UserSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["refresh"] = self.context["refresh"]
        representation["access"] = self.context["access"]
        return representation


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken.for_user(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return UserAuthSerializer(self.user, context=data).data
