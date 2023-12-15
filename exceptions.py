from flask import Flask, jsonify

app = Flask(__name__)

class HttpException(Exception):
    def __init__(self, success: bool, status: int, result: str, message: str, errors=None):
        super().__init__(message)
        self.success = success
        self.status = status
        self.result = result
        self.message = message
        self.errors = errors if errors is not None else {}

def handle_http_exception(error):
    response = jsonify({"success": error.success, "status": error.status, "result": error.result, "message": error.message, "errors": error.errors})
    return response