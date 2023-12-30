class ApiResponse:
    def __init__(self, success: bool, status: int, result: str, message: str,
                 data=None, meta=None, datatables=None):
        """
        Represents an API response.

        Args:
            success (bool): Indicates whether the API request was successful.
            status (int): The status code of the API response.
            result (str): The result of the API request.
            message (str): The message associated with the API response.
            data (optional): Additional data returned by the API.
            meta (optional): Metadata associated with the API response.
            datatables (optional): Datatables used in the API response.
        """
        self.success = success
        self.status = status
        self.result = result
        self.message = message
        self.data = data if data is not None else {}
        self.meta = meta
        self.datatables = datatables

def api_response(success: bool, response_status: int, result: str, message: str,
                 data=None, meta=None, datatables=None):
    return ApiResponse(success, response_status, result, message, data, meta, datatables)
