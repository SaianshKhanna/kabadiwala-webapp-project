from flask import Blueprint
from categories import SCRAP_CATEGORIES
from utils import response

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")

@categories_bp.get("")
def get_categories():
    return response(SCRAP_CATEGORIES, "Categories retrieved")
