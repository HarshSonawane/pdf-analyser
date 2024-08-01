from django.db import models
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, Permission
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from app.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
          """
          Create and save a user with the given email and password.
          """
          if not email:
              raise ValueError(_("The Email must be set"))
          email = self.normalize_email(email)
          user = self.model(email=email, **extra_fields)
          user.set_password(password)
          user.save()
          return user

    def create_superuser(self, email, password, **extra_fields):
          """
          Create and save a SuperUser with the given email and password.
          """
          extra_fields.setdefault("is_staff", True)
          extra_fields.setdefault("is_superuser", True)
          extra_fields.setdefault("is_active", True)

          if extra_fields.get("is_staff") is not True:
              raise ValueError(_("Superuser must have is_staff=True."))
          if extra_fields.get("is_superuser") is not True:
              raise ValueError(_("Superuser must have is_superuser=True."))
          return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    dob  = models.DateField(null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        verbose_name=_('groups'),
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'),
    )

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    objects = UserManager()

    def __str__(self):
        return self.phone
