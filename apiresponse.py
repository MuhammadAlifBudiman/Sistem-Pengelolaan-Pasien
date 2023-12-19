class ApiResponse:
    def __init__(self, success: bool, status: int, result: str, message: str,
                 data=None, meta=None, draw: int = None, start: int = None, length: int = None, records_total: int = None, records_filtered: int = None):
        self.success = success
        self.status = status
        self.result = result
        self.message = message
        self.data = data if data is not None else {}
        self.meta = meta
        self.draw = draw
        self.start = start
        self.length = length
        self.recordsTotal = records_total
        self.recordsFiltered = records_filtered

def api_response(success: bool, response_status: int, result: str, message: str,
                 data=None, meta=None, draw: int = None, start: int = None, length: int = None, records_total: int = None, records_filtered: int = None):
    return ApiResponse(success, response_status, result, message, data, meta, draw, start, length, records_total, records_filtered)
