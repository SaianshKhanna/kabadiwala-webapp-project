from datetime import datetime
from extensions import db

class ScrapRequest(db.Model):
    __tablename__ = "requests"

    request_id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey("listings.listing_id"), nullable=False, index=True)
    recycler_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    offered_price_per_kg = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.Enum("pending", "accepted", "rejected", "completed", name="request_status"),
                       default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    listing = db.relationship("Listing", back_populates="requests")
    recycler = db.relationship("User", back_populates="requests")

    def to_dict(self):
        return {
            "request_id": self.request_id,
            "listing_id": self.listing_id,
            "listing_category": self.listing.category if self.listing else None,
            "collector_id": self.listing.collector_id if self.listing else None,
            "recycler_id": self.recycler_id,
            "recycler_name": self.recycler.full_name if self.recycler else None,
            "offered_price_per_kg": self.offered_price_per_kg,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
