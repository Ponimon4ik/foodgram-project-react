from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError

special_keys = ['non_field_errors', 'following', ]


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        custom_error_response = {}
        keys = exc.detail.keys()
        for key in keys:
            if key in special_keys:
                custom_error_response['errors'] = exc.detail[key][0]
                response.data = custom_error_response
        return response
    return response
