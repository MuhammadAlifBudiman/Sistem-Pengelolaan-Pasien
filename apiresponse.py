# apiresponse.py
# This module defines the ApiResponse class and a helper function for standardizing API responses.

class ApiResponse:
    def __init__(self, success: bool, status: int, result: str, message: str,
                 data=None, meta=None, datatables=None):
        """
        Represents a standardized API response object.

        Args:
            success (bool): Indicates if the API request was successful (True/False).
            status (int): HTTP status code of the API response (e.g., 200, 404).
            result (str): Short result indicator (e.g., 'success', 'error').
            message (str): Human-readable message describing the response.
            data (optional): Main data payload returned by the API (default: empty dict if None).
            meta (optional): Additional metadata (e.g., pagination info, etc.).
            datatables (optional): Data formatted for datatables (if applicable).
        """
        # Set the success flag (True if request succeeded, else False)
        self.success = success
        # Set the HTTP status code
        self.status = status
        # Set the result string
        self.result = result
        # Set the message string
        self.message = message
        # Set the data payload, default to empty dict if not provided
        self.data = data if data is not None else {}
        # Set the meta information (optional)
        self.meta = meta
        # Set the datatables information (optional)
        self.datatables = datatables


def api_response(success: bool, response_status: int, result: str, message: str,
                 data=None, meta=None, datatables=None):
    """
    Helper function to create an ApiResponse object.

    Args:
        success (bool): Indicates if the API request was successful.
        response_status (int): HTTP status code of the API response.
        result (str): Short result indicator.
        message (str): Human-readable message.
        data (optional): Main data payload.
        meta (optional): Additional metadata.
        datatables (optional): Data for datatables.

    Returns:
        ApiResponse: An instance of ApiResponse with the provided parameters.
    """
    return ApiResponse(success, response_status, result, message, data, meta, datatables)
