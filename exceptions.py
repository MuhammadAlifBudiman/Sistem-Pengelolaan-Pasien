# exceptions.py
# This module defines a custom HTTP exception class and its handler for use in a Flask application.

# Import Flask and jsonify for creating the app and formatting JSON responses
from flask import Flask, jsonify

app = Flask(__name__)  # Initialize the Flask application instance


class HttpException(Exception):
    """
    Custom exception class to represent HTTP errors in a Flask application.

    Attributes:
        success (bool): Indicates whether the request was successful or not.
        status (int): The HTTP status code to return.
        result (str): The result or type of the request (e.g., 'error').
        message (str): A human-readable error message.
        errors (dict): Additional error details (optional).
    """

    def __init__(self, success: bool, status: int, result: str, message: str, errors=None):
        """
        Initialize the HttpException instance.

        Args:
            success (bool): Success flag (usually False for errors).
            status (int): HTTP status code (e.g., 400, 404, 500).
            result (str): Result type or label (e.g., 'error').
            message (str): Description of the error.
            errors (dict, optional): Additional error details. Defaults to empty dict if not provided.
        """
        super().__init__(message)  # Call the base Exception constructor with the error message
        self.success = success  # Set the success flag
        self.status = status    # Set the HTTP status code
        self.result = result    # Set the result type
        self.message = message  # Set the error message
        self.errors = errors if errors is not None else {}  # Set additional error details


def handle_http_exception(error):
    """
    Flask error handler for HttpException.

    Args:
        error (HttpException): The exception instance to handle.

    Returns:
        tuple: A Flask response object (JSON) and the HTTP status code.
    """
    response = jsonify({
        "success": error.success,
        "status": error.status,
        "result": error.result,
        "message": error.message,
        "errors": error.errors
    }), error.status  # Return the JSON response and status code
    return response
