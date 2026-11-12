from datetime import datetime
from extensions import db

class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("collector", "recycler", name="user_role"), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    listings = db.relationship("Listing", back_populates="collector", cascade="all, delete-orphan")
    rates = db.relationship("RecyclerRate", back_populates="recycler", cascade="all, delete-orphan")
    requests = db.relationship("ScrapRequest", back_populates="recycler", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "location": self.location,
            "created_at": self.created_at.isoformat(),
        }
