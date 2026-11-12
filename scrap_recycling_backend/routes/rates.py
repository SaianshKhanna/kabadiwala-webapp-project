from flask import Blueprint, request
from extensions import db
from models.rate import RecyclerRate
from utils import response, error, current_user, role_required, validate_category

rates_bp = Blueprint("rates", __name__, url_prefix="/api/rates")

@rates_bp.get("")
def get_rates():
    query = RecyclerRate.query
    category = request.args.get("category")
    if category:
        if not validate_category(category): return error("Invalid scrap category")
        query = query.filter_by(category=category)
    return response([x.to_dict() for x in query.order_by(RecyclerRate.updated_at.desc()).all()])

@rates_bp.post("")
@role_required("recycler")
def create_rate():
    data = request.get_json(silent=True) or {}
    if not all(k in data for k in ("category", "price_per_kg")):
        return error("category and price_per_kg are required")
    if not validate_category(data["category"]): return error("Invalid scrap category")
    try:
        price = float(data["price_per_kg"])
        minimum = float(data.get("minimum_quantity_kg", 1))
        if price <= 0 or minimum <= 0: raise ValueError()
    except (ValueError, TypeError):
        return error("Price and minimum quantity must be greater than zero")
    item = RecyclerRate(recycler_id=current_user().user_id, category=data["category"],
                        price_per_kg=price, minimum_quantity_kg=minimum, conditions=data.get("conditions"))
    db.session.add(item); db.session.commit()
    return response(item.to_dict(), "Rate created", 201)

@rates_bp.patch("/<int:rate_id>")
@role_required("recycler")
def update_rate(rate_id):
    item = RecyclerRate.query.get_or_404(rate_id)
    if item.recycler_id != current_user().user_id: return error("You can only edit your own rates", 403)
    data = request.get_json(silent=True) or {}
    if "category" in data:
        if not validate_category(data["category"]): return error("Invalid scrap category")
        item.category = data["category"]
    for field in ("price_per_kg", "minimum_quantity_kg"):
        if field in data:
            try:
                value = float(data[field])
                if value <= 0: raise ValueError()
                setattr(item, field, value)
            except (ValueError, TypeError): return error(f"{field} must be greater than zero")
    if "conditions" in data: item.conditions = data["conditions"]
    db.session.commit()
    return response(item.to_dict(), "Rate updated")

@rates_bp.delete("/<int:rate_id>")
@role_required("recycler")
def delete_rate(rate_id):
    item = RecyclerRate.query.get_or_404(rate_id)
    if item.recycler_id != current_user().user_id: return error("You can only delete your own rates", 403)
    db.session.delete(item); db.session.commit()
    return response(message="Rate deleted")
