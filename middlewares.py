from functools import wraps
from utils import get_authorization, check_user_session
from exceptions import HttpException
from flask import redirect, url_for

def validate_token_api(secret_key, token_key, db):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = get_authorization(token_key)

            if token:
                decoded_token = check_user_session(token, secret_key, db)

                if decoded_token:
                    return func(decoded_token, *args, **kwargs)
                else:
                    raise HttpException(False, 401, "Failed", "Invalid Session")
            else:
                raise HttpException(False, 401, "Failed", "Invalid or missing token")

        return wrapper
    return decorator


def validate_token_template(secret_key, token_key, db, allow_guest=False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = get_authorization(token_key)

            if token:
                decoded_token = check_user_session(token, secret_key, db)

                if decoded_token:
                    return func(decoded_token, *args, **kwargs)
                else:
                    # Token is invalid, but we allow guest access
                    if allow_guest:
                        return func(None, *args, **kwargs)
                    else:
                        # Redirect to login if guest access is not allowed
                        return redirect(url_for('login'))
            else:
                # Token is missing, but we allow guest access
                if allow_guest:
                    return func(None, *args, **kwargs)
                else:
                    # Redirect to login if guest access is not allowed
                    return redirect(url_for('login'))

        return wrapper
    return decorator

def authorized_roles_api(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(decoded_token, *args, **kwargs):
            user_roles = decoded_token.get("role", [])
            has_required_role = any(required_role in user_roles for required_role in roles)

            if has_required_role:
                return func(decoded_token, *args, **kwargs)
            else:
                raise HttpException(False, 403, "Failed", "Unauthorized Access")

        return wrapper
    return decorator

def authorized_roles_template(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(decoded_token, *args, **kwargs):
            user_roles = decoded_token.get("role", [])
            has_required_role = any(required_role in user_roles for required_role in roles)

            if has_required_role:
                return func(decoded_token, *args, **kwargs)
            else:
                return redirect(url_for('login'))
        return wrapper
    return decorator