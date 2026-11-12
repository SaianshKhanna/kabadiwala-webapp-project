from flask import Blueprint, request
from extensions import db
from models.listing import Listing
from models.request import ScrapRequest
from utils import response, error, current_user, role_required

requests_bp = Blueprint("requests", __name__, url_prefix="/api/requests")

@requests_bp.post("")
@role_required("recycler")
def create_request():
    data = request.get_json(silent=True) or {}
    if not data.get("listing_id") or data.get("offered_price_per_kg") is None:
        return error("listing_id and offered_price_per_kg are required")
    listing = Listing.query.get(data["listing_id"])
    if not listing or listing.status != "available": return error("Available listing not found", 404)
    if listing.collector_id == current_user().user_id: return error("You cannot request your own listing")
    try:
        price = float(data["offered_price_per_kg"])
        if price <= 0: raise ValueError()
    except (ValueError, TypeError): return error("offered_price_per_kg must be greater than zero")
    duplicate = ScrapRequest.query.filter_by(listing_id=listing.listing_id, recycler_id=current_user().user_id, status="pending").first()
    if duplicate: return error("You already have a pending request for this listing", 409)
    item = ScrapRequest(listing_id=listing.listing_id, recycler_id=current_user().user_id,
                        offered_price_per_kg=price, message=data.get("message"))
    db.session.add(item); db.session.commit()
    return response(item.to_dict(), "Request sent", 201)

@requests_bp.get("/received")
@role_required("collector")
def received_requests():
    items = ScrapRequest.query.join(Listing).filter(Listing.collector_id == current_user().user_id).order_by(ScrapRequest.created_at.desc()).all()
    return response([x.to_dict() for x in items])

@requests_bp.get("/sent")
@role_required("recycler")
def sent_requests():
    items = ScrapRequest.query.filter_by(recycler_id=current_user().user_id).order_by(ScrapRequest.created_at.desc()).all()
    return response([x.to_dict() for x in items])

@requests_bp.patch("/<int:request_id>")
@role_required("collector", "recycler")
def update_request(request_id):
    item = ScrapRequest.query.get_or_404(request_id)
    user = current_user()
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if not new_status: return error("status is required")
    if user.role == "collector":
        if item.listing.collector_id != user.user_id: return error("This request is not for your listing", 403)
        if new_status not in ("accepted", "rejected"): return error("Collectors can accept or reject requests")
        if item.status != "pending": return error("Only pending requests can be accepted or rejected", 409)
        item.status = new_status
        if new_status == "accepted":
            item.listing.status = "closed"
    else:
        if item.recycler_id != user.user_id: return error("You can only update your own requests", 403)
        if new_status != "completed": return error("Recyclers can only mark accepted requests as completed")
        if item.status != "accepted": return error("Only accepted requests can be completed", 409)
        item.status = "completed"
    db.session.commit()
    return response(item.to_dict(), "Request status updated")
