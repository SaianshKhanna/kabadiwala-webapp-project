import os
import uuid
from functools import wraps
from flask import jsonify, session, current_app, request
from werkzeug.utils import secure_filename
from models.user import User
from categories import SCRAP_CATEGORIES

ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def response(data=None, message="OK", status=200):
    return jsonify({"success": True, "message": message, "data": data}), status

def error(message, status=400, details=None):
    body = {"success": False, "message": message}
    if details is not None:
        body["errors"] = details
    return jsonify(body), status

def current_user():
    user_id = session.get("user_id")
    return User.query.get(user_id) if user_id else None

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            return error("Login required", 401)
        return fn(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            user = current_user()
            if user.role not in roles:
                return error("You do not have permission to perform this action", 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def validate_category(category):
    return category in SCRAP_CATEGORIES

def save_listing_image(file):
    if not file or not file.filename:
        return None, "No image selected"
    filename = secure_filename(file.filename)
    if "." not in filename or filename.rsplit(".", 1)[1].lower() not in ALLOWED_IMAGE_EXTENSIONS:
        return None, "Only PNG, JPG, JPEG and WEBP images are allowed"
    extension = filename.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{extension}"
    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, unique_name))
    return unique_name, None

def json_or_form():
    return request.get_json(silent=True) or request.form.to_dict()
