import base64
import pyotp
import urllib.parse


from django.contrib.auth import login, get_user_model

from django.conf import settings


from decouple import config
from loguru import logger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from rest_framework.decorators import action

from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema

from library.utils import (
    serializer_errors,
    error_400,
    error_404,
    generateKey,
)

from users.serializers import (
    UserSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    OTPVerificationSerializer,
    EmailandPhoneNumberSerializer,
    ResetPasswordSerializer,
    ConfirmResetTokenSerializer,
    SendOTPSerializer,
    GetEmailSerializer,
    AdminRegistrationSerializer,
    UserRegistrationSerializer,
)

from users.models import User, Platform


from users.services import (
    generate_otp,
    generate_magic_link_otp,
    send_user_verification_email,
    send_user_reset_password_email,
    send_user_magic_login_email,
)


domain = config("domain")

User = get_user_model()


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class AuthViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all().order_by("-id")
    serializer_class = UserSerializer
    http_method_names = ["get", "post", "head", "patch"]

    @extend_schema(request=AdminRegistrationSerializer)
    @action(detail=False, methods=["post"],permission_classes=[AllowAny])
    def create_internal_admin(self, request):
        user = self.request.user

        serializer = AdminRegistrationSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            email = result["email"]

            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            
            user_data = UserSerializer(user).data
            login(request, user)

            response = Response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "Admin User Created Sucessful",
                    "user_info": user_data,
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "access_duration": settings.SIMPLE_JWT[
                            "ACCESS_TOKEN_LIFETIME"
                        ],
                    },
                },
                status=status.HTTP_200_OK,
            )

            return response
       

        else:
            default_errors = serializer.errors
            error_message = serializer_errors(default_errors)

            return error_400(error_message)

    @extend_schema(request=UserRegistrationSerializer)
    @action(
        detail=False,
        methods=["post"],
        authentication_classes=[],
        permission_classes=[AllowAny],
    )
    def create_user(self, request):
        user = self.request.user

        serializer = UserRegistrationSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            email = result["email"]

            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user)

            user_data = UserSerializer(user).data
            login(request, user)

            response = Response(
                {
                    "code": 200,
                    "status": "success",
                    "message": "User Created Sucessful",
                    "user_info": user_data,
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                        "access_duration": settings.SIMPLE_JWT[
                            "ACCESS_TOKEN_LIFETIME"
                        ],
                    },
                },
                status=status.HTTP_200_OK,
            )

            return response

        else:
            default_errors = serializer.errors
            error_message = serializer_errors(default_errors)

            return error_400(error_message)

    @extend_schema(request=LoginSerializer)
    @action(
        detail=False,
        methods=["post"],
        authentication_classes=[],
        permission_classes=[AllowAny],
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            try:
                user = User.objects.get(email=email.lower())
                refresh = RefreshToken.for_user(user)
            except:
                return error_400("User does not exist")

            if user.is_verified:
                if user.is_active:
                    if user.check_password(password):
                        the_serializer = UserSerializer
                        user_data = the_serializer(user).data
                        login(request, user)

                        response = Response(
                            {
                                "code": 200,
                                "status": "success",
                                "message": "Login Sucessful",
                                "user_info": user_data,
                                "token": {
                                    "refresh": str(refresh),
                                    "access": str(refresh.access_token),
                                    "access_duration": settings.SIMPLE_JWT[
                                        "ACCESS_TOKEN_LIFETIME"
                                    ],
                                },
                            },
                            status=status.HTTP_200_OK,
                        )

                        return response

                    else:
                        return error_400("Incorrect Email/Password Inserted")

                else:
                    return error_400("User is not active. Kindly contact your admin")

            else:
                try:
                    OTP_CODE = generate_otp(email, verification=True)
                    ACCESS_TOKEN = str(refresh.access_token)
                    VERIFICATION_URL = f"{settings.FRONTEND_VERIFY_URL}?otp={OTP_CODE}&token={ACCESS_TOKEN}"
                    MESSAGE = f"Your verification url is {VERIFICATION_URL}."

                    logger.info(MESSAGE)
                    payload = {
                        "link": VERIFICATION_URL,
                        "user_first_name": user.first_name,
                        "user_email": email,
                    }
                   
                    # send_user_verification_email(payload) #Add to a background task
                    logger.info("Kindly check your mail to reset your password")
                    return Response(
                        {
                            "code": 406,
                            "status": "success",
                            "message": "User is not verified. Kindly check email for verification link",
                        },
                        status=status.HTTP_406_NOT_ACCEPTABLE,
                    )
                except User.DoesNotExist:
                    return error_404("User with the email does not exist")

        else:
            default_errors = serializer.errors
            error_message = serializer_errors(default_errors)
            return error_400(error_message)

