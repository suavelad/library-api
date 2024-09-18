from rest_framework import status, serializers
from rest_framework.response import Response
from django.http import JsonResponse


def error_500(request):
    """
    NB: The debug settings need to be set to False for this to work
    """

    message = "An error occurred, call Sunday"
    print(request)
    # send_mail to developer to handle error
    response = JsonResponse(data={"message": message, "status_code": 404})
    response.status_code = 500
    return response


def error_401(message):
    return Response(
        {
            "code": status.HTTP_401_UNAUTHORIZED,
            "status": "error",
            "message": message,
        },
        status=status.HTTP_401_UNAUTHORIZED,
    )


def error_403(message):
    return Response(
        {
            "code": status.HTTP_403_FORBIDDEN,
            "status": "error",
            "message": message,
        },
        status=status.HTTP_403_FORBIDDEN,
    )


def error_400(message):
    return Response(
        {
            "code": status.HTTP_400_BAD_REQUEST,
            "status": "error",
            "message": message,
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


def serializer_error_400(message):
    return serializers.ValidationError(
        {"code": 400, "status": "error", "message": message}
    )


def error_404(message):
    return Response(
        {
            "code": status.HTTP_404_NOT_FOUND,
            "status": "error",
            "message": message,
        },
        status=status.HTTP_404_NOT_FOUND,
    )


def error_406(message):
    return Response(
        {
            "code": status.HTTP_406_NOT_ACCEPTABLE,
            "status": "error",
            "message": message,
        },
        status=status.HTTP_406_NOT_ACCEPTABLE,
    )
