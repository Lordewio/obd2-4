from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from .job import JobStatus

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    mechanic_id = Column(String, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    rating = Column(Float)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="reviews")
    mechanic = relationship("User", foreign_keys=[mechanic_id], back_populates="received_reviews")
    job = relationship("Job", back_populates="reviews")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "mechanic_id": self.mechanic_id,
            "job_id": self.job_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status.value
        }

    def __repr__(self):
        return f"<Review {self.id} - Rating {self.rating} - Mechanic {self.mechanic_id}>"
