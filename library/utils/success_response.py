from rest_framework.response import Response
from rest_framework import status

def success_20X(data,response_status):
    return Response(
        {
            "code": response_status,
            "message": "successful",
            "data": data,
        },
        status=response_status,
    )


def success_200(data):
    return Response(
        {
            "code": status.HTTP_200_OK,
            "message": "successful",
            "data": data,
        },
        status=status.HTTP_200_OK,
    )
