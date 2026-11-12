from flask import Blueprint, request, url_for
from extensions import db
from models.listing import Listing
from utils import response, error, current_user, login_required, role_required, validate_category, save_listing_image

listings_bp = Blueprint("listings", __name__, url_prefix="/api/listings")

def listing_payload(item):
    return item.to_dict(request.host_url.rstrip("/"))

@listings_bp.post("")
@role_required("collector")
def create_listing():
    user = current_user()
    data = request.form.to_dict() if request.content_type and request.content_type.startswith("multipart/form-data") else (request.get_json(silent=True) or {})
    required = ["category", "quantity_kg", "pickup_area", "contact_method"]
    missing = [x for x in required if not str(data.get(x, "")).strip()]
    if missing:
        return error("Missing required fields", 400, {"missing": missing})
    if not validate_category(data["category"]):
        return error("Invalid scrap category")
    try:
        quantity = float(data["quantity_kg"])
        if quantity <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return error("quantity_kg must be a number greater than zero")
    image_name = None
    if "image" in request.files:
        image_name, image_error = save_listing_image(request.files["image"])
        if image_error:
            return error(image_error)
    item = Listing(
        collector_id=user.user_id, category=data["category"], quantity_kg=quantity,
        description=data.get("description"), image_path=image_name,
        pickup_area=data["pickup_area"].strip(), contact_method=data["contact_method"].strip()
    )
    db.session.add(item)
    db.session.commit()
    return response(listing_payload(item), "Listing created", 201)

@listings_bp.get("")
def browse_listings():
    query = Listing.query.filter_by(status="available")
    category = request.args.get("category")
    if category:
        if not validate_category(category):
            return error("Invalid scrap category")
        query = query.filter_by(category=category)
    items = query.order_by(Listing.created_at.desc()).all()
    return response([listing_payload(x) for x in items])

@listings_bp.get("/my")
@role_required("collector")
def my_listings():
    items = Listing.query.filter_by(collector_id=current_user().user_id).order_by(Listing.created_at.desc()).all()
    return response([listing_payload(x) for x in items])

@listings_bp.get("/<int:listing_id>")
@login_required
def get_listing(listing_id):
    item = Listing.query.get_or_404(listing_id)
    return response(listing_payload(item))

@listings_bp.patch("/<int:listing_id>")
@role_required("collector")
def update_listing(listing_id):
    item = Listing.query.get_or_404(listing_id)
    if item.collector_id != current_user().user_id:
        return error("You can only edit your own listings", 403)
    data = request.form.to_dict() if request.content_type and request.content_type.startswith("multipart/form-data") else (request.get_json(silent=True) or {})
    if "category" in data:
        if not validate_category(data["category"]):
            return error("Invalid scrap category")
        item.category = data["category"]
    if "quantity_kg" in data:
        try:
            quantity = float(data["quantity_kg"])
            if quantity <= 0: raise ValueError()
            item.quantity_kg = quantity
        except (ValueError, TypeError):
            return error("quantity_kg must be a number greater than zero")
    for field in ("description", "pickup_area", "contact_method", "status"):
        if field in data:
            if field == "status" and data[field] not in ("available", "closed", "cancelled"):
                return error("Invalid listing status")
            setattr(item, field, data[field])
    if "image" in request.files:
        image_name, image_error = save_listing_image(request.files["image"])
        if image_error: return error(image_error)
        item.image_path = image_name
    db.session.commit()
    return response(listing_payload(item), "Listing updated")

@listings_bp.delete("/<int:listing_id>")
@role_required("collector")
def delete_listing(listing_id):
    item = Listing.query.get_or_404(listing_id)
    if item.collector_id != current_user().user_id:
        return error("You can only delete your own listings", 403)
    db.session.delete(item)
    db.session.commit()
    return response(message="Listing deleted")
