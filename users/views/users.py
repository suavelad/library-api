from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema
from loguru import logger

from users.serializers import UserSerializer, GetPatchUserSerializer

from library.utils import (
    CustomPagination,
    error_400,
    error_401,
    serializer_errors,
    serializer_error_400,
    get_paginated_output,
    success_200,
)

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    http_method_names = ["get", "post", "head", "patch", "delete"]

    def get_queryset(self):
        user = self.request.user
        pk = self.kwargs.get("pk", None)

        if pk:
            the_user = User.objects.filter(id=pk).first()

            if the_user == user:
                return the_user
            else:
                raise serializer_error_400("User not found or not allowed")
        else:
            return self.queryset

    def list(self, request, *args, **kwargs):
        user = self.request.user
        if user.user_type != User.ADMIN:
            return error_401("User is Unauthorized")

        users = self.get_queryset()
        paginated_output = get_paginated_output(users, UserSerializer, request)
        return success_200(paginated_output)

    @action(detail=False, methods=["get"])
    def me(self, request):
        user = request.user
        if user:
            user = User.objects.get(email=user.email)
            refresh = RefreshToken.for_user(user)
            if user.is_verified:
                if user.is_active:
                    the_serializer = UserSerializer
                    user_data = the_serializer(user).data

                    data_response = {
                        "code": status.HTTP_200_OK,
                        "status": "success",
                        "message": "User profile",
                        "user_info": user_data,
                        "token": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                            "access_duration": settings.SIMPLE_JWT[
                                "ACCESS_TOKEN_LIFETIME"
                            ],
                        },
                    }

                    response = Response(data_response, status=status.HTTP_200_OK)
                    return response

                else:
                    return error_401("User is not active. Kindly contact your admin")

            else:
                return Response(
                    {
                        "code": 401,
                        "status": "error",
                        "message": "User not verified.Kindly check your mail for your verification code",
                        "token": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                            "access_duration": settings.SIMPLE_JWT[
                                "ACCESS_TOKEN_LIFETIME"
                            ],
                        },
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        else:
            return error_401("User does not exist")

    @extend_schema(exclude=True)
    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(request=GetPatchUserSerializer)
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True

        user = request.user

        serializer = GetPatchUserSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            first_name = data.get("first_name", None)
            last_name = data.get("last_name", None)
            middle_name = data.get("middle_name", None)
            phone = data.get("phone", None)
            country = data.get("country", None)
            address = data.get("address", None)
            dob = data.get("dob", None)
            gender = data.get("gender", None)
            is_active = data.get("is_active", None)
            user_type = data.get("user_type", None)
            is_email_verified = data.get("is_email_verified", None)
            is_phone_number_verified = data.get("is_phone_number_verified", None)
            is_verified = data.get("is_verified", None)

            instance = User.objects.filter(id=kwargs["pk"]).first()
            if not instance:
                return error_400("Invalid id used")

            if first_name:
                instance.first_name = first_name

            if last_name:
                instance.last_name = last_name

            if middle_name:
                instance.middle_name = middle_name

            if phone:
                instance.phone = phone

            if country:
                instance.country = country

            if address:
                instance.address = address

            if gender:
                instance.gender = gender

            if dob:
                instance.dob = dob

            if user.user_type == User.ADMIN:
                if is_active:
                    instance.is_active = is_active

                if is_email_verified:
                    instance.is_email_verified = is_email_verified

                if is_phone_number_verified:
                    instance.is_phone_number_verified = is_phone_number_verified

                if is_verified:
                    instance.is_verified = is_verified

                if user_type:
                    instance.user_type = user_type

            instance.save()

            return Response(serializer.data)

        else:
            default_errors = serializer.errors
            error_message = serializer_errors(default_errors)
            return error_400(error_message)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.email = f"{instance.email}__deleted"
        instance.phone = f"{instance.phone}__deleted"
        instance.is_active = False
        instance._is_verified = False
        instance.is_email_verified = False
        instance.is_phone_number_verified = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
