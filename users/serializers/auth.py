from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from loguru import logger


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class GetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class OTPVerificationSerializer(serializers.Serializer):
    otp_code = serializers.CharField(required=True)
    user_verify = serializers.BooleanField(required=False)


class EmailandPhoneNumberSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=["email", "sms"], required=True)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)


class SendOTPSerializer(serializers.Serializer):
    platform = serializers.ChoiceField(choices=["email", "sms"], required=True)


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    has_partnership = serializers.BooleanField(required=False)


class ConfirmResetTokenSerializer(serializers.Serializer):
    otp_code = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
