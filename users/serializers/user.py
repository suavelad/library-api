from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from users.models import User

from loguru import logger

from library.utils import serializer_error_400


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            "is_active",
            "is_verified",
            "is_staff",
            "password",
            "is_superuser",
            "user_permissions",
            "groups",
            "username",
        )


class UserRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    dob = serializers.CharField(required=False)
    gender = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    image = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        password = validated_data.pop("password")
        email = validated_data["email"]

        existing_user = User.objects.filter(email=email).first()

        if not existing_user:
            user = User.objects.create(**validated_data)

            user.set_password(password)
            user.is_verified = True   #This is because it is a demo app, ideally, i should make it false then used the verify api to vaildate the user
            user.is_active = True
            user.user_type = User.USER
            user.save()

            return validated_data

        else:
            raise serializer_error_400("User already exist")


class AdminRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    gender = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user
        password = validated_data.pop("password")
        email = validated_data["email"]

        existing_user = User.objects.filter(email=email).first()

        if not existing_user:
            admin = User.objects.create(**validated_data)

            admin.set_password(password)

            admin.is_verified = True   #This is because it is a demo app, ideally, i should make it false then used the verify api to vaildate the user
            admin.is_active = True
            admin.user_type = User.ADMIN
            admin.created_by = user.id
            admin.save()

            return validated_data

        else:
            raise serializer_error_400("User already exist")


class GetPatchUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    middle_name = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    dob = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE, required=False)
    is_email_verified = serializers.BooleanField(required=False)
    is_phone_number_verified = serializers.BooleanField(required=False)
    is_verified = serializers.BooleanField(required=False)
