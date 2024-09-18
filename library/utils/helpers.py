import threading, re
import random
import string
import secrets
from datetime import datetime
from enum import Enum

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from decouple import config
from loguru import logger

page_size_query_param = config("page_size_query_param")
page_query_param = config("page_query_param")

from .error_response import error_401, error_403


# This class returns the string needed to generate the key
class generateKey:
    @staticmethod
    def returnValue(phone):
        return f"{phone}{datetime.date(datetime.now())}{settings.SECRET_KEY}"


class CustomPagination(PageNumberPagination):
    page_size_query_param = page_size_query_param
    page_query_param = page_query_param
    # max_page_size = 20

    def get_paginated_response(self, data):
        return {
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "count": self.page.paginator.count,
            # "page_size": self.page.paginator.page_size,
            "total_pages": self.page.paginator.num_pages,
            "results": data,
        }


class ViewsetMixin:
    def paginate_results(self, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        """
        Override method to perform a "logic" destroy.
        """
        instance.archive()


def get_random_string(length):
    # choose from all letter and digits
    letters = string.ascii_letters + string.digits
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


def generate_random_code(length):
    letters = string.ascii_letters + string.digits
    main_str = "".join(random.choice(letters) for i in range(length))
    return main_str


def serializer_errors(default_errors):
    logger.debug("Errors:", default_errors)
    error_messages = ""
    for field_name, field_errors in default_errors.items():
        if field_errors[0].code == "unique":
            error_messages += f"{field_name} already exists, "
        else:
            error_messages += f"{field_name} is {field_errors[0].code}, "
    return error_messages


def format_phone_number(phone_number):
    if not phone_number or len(phone_number) < 2:
        return None

    if len(phone_number) > 2 and phone_number[0] == "+":
        return phone_number[1:]

    elif len(phone_number) > 2 and phone_number[:3] == "234":
        return phone_number

    elif len(phone_number) > 2 and phone_number[:3] != "234" and phone_number[0] != "+":
        return f"234{phone_number[1:]}"


def validate_phone(value):
    pattern = re.compile(r"^\+?1?\d{9,15}$")
    if not bool(pattern.match(value)):
        raise ValidationError(
            _(
                "Invalid! Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            ),
            params={"value": value},
        )


def custom_normalize_email(email):
    return email.strip().lower()


def get_paginated_output(request_model_data, request_model_serializer, request):
    paginator = CustomPagination()
    result_page = paginator.paginate_queryset(request_model_data, request)
    serialized_data = request_model_serializer(result_page, many=True).data
    output = paginator.get_paginated_response(serialized_data)
    return output


def remove_special_character(name):
    formatted_name = re.sub(r"[^a-zA-Z.-]+", " ", str(name)).strip().replace(" ", "_")
    return str(formatted_name.lower())


class CustomEnum(Enum):
    @classmethod
    def values(cls):
        return [c.value for c in cls]

    @classmethod
    def choices(cls):
        return [(c.value, c.value) for c in cls]
