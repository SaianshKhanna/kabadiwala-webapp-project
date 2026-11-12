from datetime import datetime
from extensions import db

class Listing(db.Model):
    __tablename__ = "listings"

    listing_id = db.Column(db.Integer, primary_key=True)
    collector_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    category = db.Column(db.String(60), nullable=False, index=True)
    quantity_kg = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(500))
    pickup_area = db.Column(db.String(255), nullable=False)
    contact_method = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Enum("available", "closed", "cancelled", name="listing_status"),
                       default="available", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    collector = db.relationship("User", back_populates="listings")
    requests = db.relationship("ScrapRequest", back_populates="listing", cascade="all, delete-orphan")

    def to_dict(self, base_url=None):
        image_url = None
        if self.image_path:
            image_url = f"{base_url}/uploads/{self.image_path}" if base_url else f"/uploads/{self.image_path}"
        return {
            "listing_id": self.listing_id,
            "collector_id": self.collector_id,
            "collector_name": self.collector.full_name if self.collector else None,
            "category": self.category,
            "quantity_kg": self.quantity_kg,
            "description": self.description,
            "image_path": self.image_path,
            "image_url": image_url,
            "pickup_area": self.pickup_area,
            "contact_method": self.contact_method,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
