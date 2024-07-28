from rest_framework.response import Response


class CustomResponse:
    """
    A utility class for generating custom success and error responses.
    """

    @staticmethod
    def success(message, data=None, status_code=200):
        """
        Generate a custom success response.

        Args:
            message (str): The success message.
            data (dict, optional): Additional data for the response. Defaults to None.
            status_code (int, optional): The HTTP status code for the response. Defaults to 200.

        Returns:
            Response: A DRF Response object with the custom success message and data.
        """
        response = {
            "status": "success",
            "message": message,
            "data": data,
        }
        response.pop("data", None) if data is None else ...
        return Response(data=response, status=status_code)

    @staticmethod
    def error(message, err_code, data=None, status_code=400):
        """
        Generate a custom error response.

        Args:
            message (str): The error message.
            err_code (str): The error code.
            data (dict, optional): Additional data for the response. Defaults to None.
            status_code (int, optional): The HTTP status code for the response. Defaults to 400.

        Returns:
            Response: A DRF Response object with the custom error message and data.
        """
        response = {
            "status": "failure",
            "message": message,
            "code": err_code,
            "data": data,
        }
        response.pop("data", None) if data is None else ...
        return Response(data=response, status=status_code)
