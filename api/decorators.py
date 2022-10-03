from functools import wraps

from apiflask import abort
from flask import current_app

from .auth import token_auth


def admin_required(f):
    """If you decorate view with this, it will ensure that the current user 
    has administrator permission."""
    @wraps(f)
    def decorator(*args, **kwargs):
        if token_auth.current_user.email != current_app.config["ADMIN_EMAIL"]:
            abort(403)
        return f(*args, **kwargs)
    return decorator
    