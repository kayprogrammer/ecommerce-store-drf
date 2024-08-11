from http import HTTPStatus
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    AuthenticationFailed,
    ValidationError,
    APIException,
)

from .responses import CustomResponse


class ErrorCode:
    """
    A class to represent various error codes as constants.
    """

    UNAUTHORIZED_USER = "unauthorized_user"
    NETWORK_FAILURE = "network_failure"
    SERVER_ERROR = "server_error"
    INVALID_ENTRY = "invalid_entry"
    INCORRECT_EMAIL = "incorrect_email"
    INCORRECT_OTP = "incorrect_otp"
    EXPIRED_OTP = "expired_otp"
    INVALID_AUTH = "invalid_auth"
    INVALID_TOKEN = "invalid_token"
    INVALID_CREDENTIALS = "invalid_credentials"
    UNVERIFIED_USER = "unverified_user"
    NON_EXISTENT = "non_existent"
    INVALID_OWNER = "invalid_owner"
    INVALID_PAGE = "invalid_page"
    INVALID_VALUE = "invalid_value"
    NOT_ALLOWED = "not_allowed"
    INVALID_DATA_TYPE = "invalid_data_type"
    INVALID_CLIENT_ID = "invalid_client_id"
    USED_COUPON = "used_coupon"


class RequestError(APIException):
    """
    A custom exception class for handling request errors.

    Attributes:
        default_detail (str): The default detail message for the exception.
        err_msg (str): The error message.
        err_code (str): The error code.
        status_code (int): The HTTP status code.
        data (dict): Additional data related to the error.
    """

    default_detail = "An error occured"

    def __init__(
        self, err_msg: str, err_code: str, status_code: int = 400, data: dict = None
    ) -> None:
        """
        Initialize a RequestError instance.

        Args:
            err_msg (str): The error message.
            err_code (str): The error code.
            status_code (int, optional): The HTTP status code. Defaults to 400.
            data (dict, optional): Additional data related to the error. Defaults to None.
        """
        self.status_code = HTTPStatus(status_code)
        self.err_code = err_code
        self.err_msg = err_msg
        self.data = data

        super().__init__()


class NotFoundError(RequestError):
    def __init__(
        self,
        err_msg: str,
        err_code: str = ErrorCode.NON_EXISTENT,
        status_code: int = 404,
        data: dict = None,
    ) -> None:
        super().__init__(err_msg, err_code, status_code, data)


def process_validation_errors(errors):
    for key in errors:
        if isinstance(errors[key], dict):
            # Recursively process nested fields
            process_validation_errors(errors[key])
        else:
            err_val = str(errors[key][0]).replace('"', "")
            errors[key] = err_val
            if isinstance(err_val, list):
                errors[key] = err_val
    return errors


def custom_exception_handler(exc, context):
    """
    A custom exception handler to handle various types of exceptions.

    Args:
        exc (Exception): The exception to handle.
        context (dict): The context in which the exception occurred.

    Returns:
        CustomResponse: A custom response object with the error details.
    """
    try:
        response = exception_handler(exc, context)
        if isinstance(exc, AuthenticationFailed):
            exc_list = str(exc).split("DETAIL: ")
            return CustomResponse.error(
                message=exc_list[-1],
                status_code=401,
                err_code=ErrorCode.UNAUTHORIZED_USER,
            )
        elif isinstance(exc, RequestError):
            return CustomResponse.error(
                message=exc.err_msg,
                data=exc.data,
                status_code=exc.status_code,
                err_code=exc.err_code,
            )
        elif isinstance(exc, ValidationError):
            errors = exc.detail
            errors = process_validation_errors(errors)

            return CustomResponse.error(
                message="Invalid Entry",
                data=errors,
                status_code=422,
                err_code=ErrorCode.INVALID_ENTRY,
            )
        else:
            print("Unknown", exc)
            return CustomResponse.error(
                message="Something went wrong!",
                status_code=(
                    response.status_code if hasattr(response, "status_code") else 500
                ),
                err_code=ErrorCode.SERVER_ERROR,
            )
    except APIException as e:
        print("Server Error: ", e)
        return CustomResponse.error(
            message="Server Error", status_code=500, err_code=ErrorCode.SERVER_ERROR
        )


class ValidationErr(RequestError):
    def __init__(
        self,
        field: str,
        message: str,
        err_msg: str = "Invalid Entry",
        err_code: str = ErrorCode.INVALID_ENTRY,
        status_code: int = 422,
    ) -> None:
        data = {field: message}
        super().__init__(err_msg, err_code, status_code, data)
