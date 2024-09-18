from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    exception_class = exc.__class__.__name__
    print("exception", exception_class)
    handlers = {
        "ValidationError": _handle_validation_error,
        # 'Http404': _handle_generic_error,
        "PermissionDenied": _handle_permission_error,
        "NotAuthenticated": _handle_authentication_error,
    }
    response = exception_handler(exc, context)
    # if response is not None:
    #     response.data['status_code'] = response.status_code
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    return response


def _handle_authentication_error(exc, context, response):
    response.data = {
        "status": False,
        "message": "Please login to proceed",
        "status_code": response.status_code,
    }
    return response


def _handle_validation_error(exc, context, response):
    message = []
    exc_codes = exc.get_codes()
    print(exc_codes)
    for key in exc_codes:
        # Exc codes = ['required, unique, invalid]
        for code in exc_codes[key]:
            key = key.replace("_", " ")
            if code == "unique":
                message.append(f"{key} is not {code}")
            else:
                message.append(f"{key} is {code}")
    response.data = {
        "status": False,
        "message": ", ".join(message),
        "status_code": response.status_code,
    }
    return response


def _handle_permission_error(exc, context, response):
    response.data = {
        "status": False,
        "message": exc.default_detail,
        "status": response.status_code,
    }
    return response
