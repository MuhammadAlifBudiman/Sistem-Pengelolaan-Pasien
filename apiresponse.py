class ApiResponse:
    def __init__(self, success: bool, status: int, result: str, message: str,
                 data=None, meta=None):
        self.success = success
        self.status = status
        self.result = result
        self.message = message
        self.data = data if data is not None else {}
        self.meta = meta

def api_response(success: bool, response_status: int, result: str, message: str,
                 data=None, meta=None):
    return ApiResponse(success, response_status, result, message, data, meta)

class DataTablesApiResponse:
    def __init__(self, draw: int, records_total: int, records_filtered: int,
                 data=None):
        self.draw = draw
        self.recordsTotal = records_total
        self.recordsFiltered = records_filtered
        self.data = data if data is not None else []

def api_response_for_datatables(draw: int, records_total: int,
                                records_filtered: int, data=None):
    return DataTablesApiResponse(draw, records_total, records_filtered, data)