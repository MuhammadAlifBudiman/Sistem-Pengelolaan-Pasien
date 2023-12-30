from flask import Flask, jsonify

app = Flask(__name__)

class HttpException(Exception):
    """
    Represents an HTTP exception.

    Attributes:
        success (bool): Indicates whether the request was successful or not.
        status (int): The HTTP status code.
        result (str): The result of the request.
        message (str): The error message.
        errors (dict): Additional error details (optional).
    """

    def __init__(self, success: bool, status: int, result: str, message: str, errors=None):
        super().__init__(message)
        self.success = success
        self.status = status
        self.result = result
        self.message = message
        self.errors = errors if errors is not None else {}

def handle_http_exception(error):
    response = jsonify({"success": error.success, "status": error.status, "result": error.result, "message": error.message, "errors": error.errors}), error.status
    return response