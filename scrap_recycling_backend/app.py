import os
from flask import Flask, jsonify, send_from_directory
from config import Config
from extensions import db
from models import User, Listing, RecyclerRate, ScrapRequest
from routes.auth import auth_bp
from routes.categories import categories_bp
from routes.listings import listings_bp
from routes.rates import rates_bp
from routes.requests import requests_bp
from routes.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(rates_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(dashboard_bp)

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    @app.get("/api/health")
    def health():
        return jsonify({"success": True, "message": "Scrap Recycling API is running"}), 200

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"success": False, "message": "Resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return jsonify({"success": False, "message": "Method not allowed"}), 405

    @app.errorhandler(413)
    def too_large(_error):
        return jsonify({"success": False, "message": "Uploaded file is too large"}), 413

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
