from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import (
    AbstractUser,
    PermissionsMixin,
)
from ..manager import CustomUserManager
from rest_framework_simplejwt.tokens import RefreshToken


class Platform:
    SMS = "sms"
    EMAIL = "email"
    WHATSAPP = "whatsapp"



class User(AbstractUser, PermissionsMixin):
    GENDER = (("male", "Male"), ("female", "Female"))

    ADMIN = "admin"
    USER = "user"

    USER_TYPE = (("ADMIN", ADMIN), ("USER", USER))

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True, db_index=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER, null=True, blank=True)
    dob = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=255, default="Nigeria")
    user_type = models.CharField(max_length=20, choices=USER_TYPE, default=USER)
    address = models.TextField(null=True, blank=True)
    is_verified = models.BooleanField(default=False, null=True, blank=True)
    is_phone_number_verified = models.BooleanField(default=False, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False, null=True, blank=True)
    is_active = models.BooleanField(default=False, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = CustomUserManager()

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name} {self.username}"

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}

