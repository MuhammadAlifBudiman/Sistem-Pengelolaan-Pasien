class ApiResponse:
    def __init__(self, success: bool, status: int, result: str, message: str,
                 data=None, meta=None, datatables=None):
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
