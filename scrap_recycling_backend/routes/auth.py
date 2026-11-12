import re
from flask import Blueprint, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.user import User
from utils import response, error, current_user, login_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    required = ["full_name", "email", "phone", "password", "role", "location"]
    missing = [key for key in required if not str(data.get(key, "")).strip()]
    if missing:
        return error("Missing required fields", 400, {"missing": missing})
    email = data["email"].strip().lower()
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return error("Enter a valid email address")
    if data["role"] not in ("collector", "recycler"):
        return error("Role must be collector or recycler")
    if len(data["password"]) < 8:
        return error("Password must contain at least 8 characters")
    if User.query.filter_by(email=email).first():
        return error("An account with this email already exists", 409)
    user = User(
        full_name=data["full_name"].strip(),
        email=email,
        phone=data["phone"].strip(),
        password_hash=generate_password_hash(data["password"]),
        role=data["role"],
        location=data["location"].strip(),
    )
    db.session.add(user)
    db.session.commit()
    return response(user.to_dict(), "Registration successful", 201)

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return error("Email and password are required")
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return error("Invalid email or password", 401)
    session.clear()
    session["user_id"] = user.user_id
    return response(user.to_dict(), "Login successful")

@auth_bp.post("/logout")
@login_required
def logout():
    session.clear()
    return response(message="Logged out successfully")

@auth_bp.get("/me")
@login_required
def me():
    return response(current_user().to_dict())
