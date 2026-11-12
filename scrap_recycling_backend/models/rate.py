from datetime import datetime
from extensions import db

class RecyclerRate(db.Model):
    __tablename__ = "recycler_rates"

    rate_id = db.Column(db.Integer, primary_key=True)
    recycler_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    category = db.Column(db.String(60), nullable=False, index=True)
    price_per_kg = db.Column(db.Float, nullable=False)
    minimum_quantity_kg = db.Column(db.Float, default=1, nullable=False)
    conditions = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    recycler = db.relationship("User", back_populates="rates")

    def to_dict(self):
        return {
            "rate_id": self.rate_id,
            "recycler_id": self.recycler_id,
            "recycler_name": self.recycler.full_name if self.recycler else None,
            "category": self.category,
            "price_per_kg": self.price_per_kg,
            "minimum_quantity_kg": self.minimum_quantity_kg,
            "conditions": self.conditions,
            "updated_at": self.updated_at.isoformat(),
        }
