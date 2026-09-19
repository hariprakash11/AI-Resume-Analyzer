from functools import wraps

from flask import (
    redirect,
    session,
    url_for,
)


def login_required(view_function):
    """
    Require an authenticated user before accessing a route.
    """

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if "user_id" not in session:
            return redirect(
                url_for("auth.login")
            )

        return view_function(
            *args,
            **kwargs
        )

    return wrapped_view