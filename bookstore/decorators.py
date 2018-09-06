from functools import wraps
from flask import abort
from flask_login import current_user
from bookstore import models


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.role_id is not 1:
            abort(403)
        return func(*args, **kwargs)
    return decorated_function
