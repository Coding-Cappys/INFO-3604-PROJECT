from functools import wraps

from flask import abort, flash, jsonify, redirect, request, url_for
from flask_jwt_extended import current_user, jwt_required


def _unauthorized_response(message, status_code):
    if request.path.startswith("/api/") or request.is_json:
        return jsonify({"message": message}), status_code
    flash(message)
    return redirect(url_for("index_views.index_page"))


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            if current_user is None:
                return _unauthorized_response("Please log in to continue.", 401)

            allowed_roles = {role.value if hasattr(role, "value") else str(role) for role in roles}
            if current_user.role.value not in allowed_roles:
                return _unauthorized_response("You do not have access to this page.", 403)

            return fn(*args, **kwargs)

        return wrapper

    return decorator


def owner_or_role_required(owner_id, *roles):
    if current_user and current_user.id == owner_id:
        return

    allowed_roles = {role.value if hasattr(role, "value") else str(role) for role in roles}
    if current_user is None or current_user.role.value not in allowed_roles:
        abort(403)
