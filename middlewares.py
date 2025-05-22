# middlewares.py
# Middleware functions for token validation and role-based authorization in a Flask application.
# Provides decorators for API and template route protection, using JWT/session tokens and user roles.

from functools import wraps
from utils import get_authorization, check_user_session
from exceptions import HttpException
from flask import redirect, url_for


def validate_token_api(secret_key, token_key, db):
    """
    Decorator for validating API requests using a token.
    - Checks for the presence of a token in the request headers.
    - Validates the token using the provided secret_key and db.
    - If valid, passes the decoded token to the wrapped function.
    - Raises HttpException if token is missing or invalid.
    Args:
        secret_key (str): Secret key for decoding the token.
        token_key (str): Header key where the token is expected.
        db: Database connection/session for session validation.
    Returns:
        function: Decorated function with token validation.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get token from request headers
            token = get_authorization(token_key)

            if token:
                # Validate token and check session
                decoded_token = check_user_session(token, secret_key, db)

                if decoded_token:
                    # Pass decoded token to the wrapped function
                    return func(decoded_token, *args, **kwargs)
                else:
                    # Invalid session
                    raise HttpException(
                        False, 401, "Failed", "Invalid Session")
            else:
                # Token missing
                raise HttpException(False, 401, "Failed",
                                    "Invalid or missing token")

        return wrapper
    return decorator


def validate_token_template(secret_key, token_key, db, allow_guest=False):
    """
    Decorator for validating template (web page) requests using a token.
    - Checks for the presence of a token in the request cookies or headers.
    - Validates the token using the provided secret_key and db.
    - If valid, passes the decoded token to the wrapped function.
    - If invalid or missing, allows guest access if allow_guest is True, otherwise redirects to login.
    Args:
        secret_key (str): Secret key for decoding the token.
        token_key (str): Header/cookie key where the token is expected.
        db: Database connection/session for session validation.
        allow_guest (bool): Whether to allow guest access if token is invalid/missing.
    Returns:
        function: Decorated function with token validation for templates.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get token from request
            token = get_authorization(token_key)

            if token:
                # Validate token and check session
                decoded_token = check_user_session(token, secret_key, db)

                if decoded_token:
                    # Pass decoded token to the wrapped function
                    return func(decoded_token, *args, **kwargs)
                else:
                    # Token is invalid, but allow guest if specified
                    if allow_guest:
                        return func(None, *args, **kwargs)
                    else:
                        # Redirect to login if guest not allowed
                        return redirect(url_for('login'))
            else:
                # Token is missing, but allow guest if specified
                if allow_guest:
                    return func(None, *args, **kwargs)
                else:
                    # Redirect to login if guest not allowed
                    return redirect(url_for('login'))

        return wrapper
    return decorator


def authorized_roles_api(roles):
    """
    Decorator for API endpoints to restrict access based on user roles.
    - Checks if the decoded_token contains any of the required roles.
    - If authorized, calls the wrapped function.
    - Otherwise, raises HttpException for unauthorized access.
    Args:
        roles (list): List of roles allowed to access the endpoint.
    Returns:
        function: Decorated function with role-based access control.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(decoded_token, *args, **kwargs):
            # Get user roles from decoded token
            user_roles = decoded_token.get("role", [])
            # Check if user has any required role
            has_required_role = any(
                required_role in user_roles for required_role in roles)

            if has_required_role:
                return func(decoded_token, *args, **kwargs)
            else:
                # Unauthorized access
                raise HttpException(
                    False, 403, "Failed", f"Unauthorized Access, required roles: {roles}")

        return wrapper
    return decorator


def authorized_roles_template(roles):
    """
    Decorator for template routes to restrict access based on user roles.
    - Checks if the decoded_token contains any of the required roles.
    - If authorized, calls the wrapped function.
    - Otherwise, redirects to login page.
    Args:
        roles (list): List of roles allowed to access the route.
    Returns:
        function: Decorated function with role-based access control for templates.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(decoded_token, *args, **kwargs):
            # Get user roles from decoded token
            user_roles = decoded_token.get("role", [])
            # Check if user has any required role
            has_required_role = any(
                required_role in user_roles for required_role in roles)

            if has_required_role:
                return func(decoded_token, *args, **kwargs)
            else:
                # Redirect to login if unauthorized
                return redirect(url_for('login'))
        return wrapper
    return decorator
