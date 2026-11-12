from flask import Blueprint, request
from extensions import db
from models.listing import Listing
from models.rate import RecyclerRate
from models.request import ScrapRequest
from models.user import User
from utils import response, error, current_user, login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api")

@dashboard_bp.get("/dashboard")
@login_required
def dashboard():
    user = current_user()
    if user.role == "collector":
        listing_count = Listing.query.filter_by(collector_id=user.user_id).count()
        request_count = ScrapRequest.query.join(Listing).filter(Listing.collector_id == user.user_id).count()
        data = {"role": user.role, "total_listings": listing_count, "requests_received": request_count}
    else:
        rate_count = RecyclerRate.query.filter_by(recycler_id=user.user_id).count()
        request_count = ScrapRequest.query.filter_by(recycler_id=user.user_id).count()
        data = {"role": user.role, "total_rates": rate_count, "requests_sent": request_count}
    return response(data)

@dashboard_bp.get("/profile")
@login_required
def get_profile():
    return response(current_user().to_dict())

@dashboard_bp.patch("/profile")
@login_required
def update_profile():
    user = current_user()
    data = request.get_json(silent=True) or {}
    allowed = ("full_name", "phone", "location")
    for field in allowed:
        if field in data:
            value = str(data[field]).strip()
            if not value: return error(f"{field} cannot be empty")
            setattr(user, field, value)
    if "email" in data:
        email = str(data["email"]).strip().lower()
        existing = User.query.filter(User.email == email, User.user_id != user.user_id).first()
        if existing: return error("Email is already in use", 409)
        if "@" not in email: return error("Enter a valid email")
        user.email = email
    db.session.commit()
    return response(user.to_dict(), "Profile updated")
