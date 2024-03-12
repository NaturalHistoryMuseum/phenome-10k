from functools import wraps

from flask import render_template
from flask_security import login_required, current_user


def requires_admin(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            return (
                render_template(
                    'errors/403.html',
                    message='You must be an administrator to access this page.',
                ),
                403,
            )
        return f(*args, **kwargs)

    return decorated_function


def requires_contributor(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if current_user.can_contribute():
            return f(*args, **kwargs)
        else:
            return (
                render_template(
                    'errors/403.html',
                    message='You must be a contributor to access this page.',
                ),
                403,
            )

    return decorated_function
