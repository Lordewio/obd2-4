from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from .job import JobStatus

class NotificationType(str, Enum):
    JOB_REQUEST = "JOB_REQUEST"
    JOB_ACCEPTED = "JOB_ACCEPTED"
    JOB_COMPLETED = "JOB_COMPLETED"
    JOB_CANCELLED = "JOB_CANCELLED"
    NEW_REVIEW = "NEW_REVIEW"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    data = Column(String, nullable=True)  # JSON string for additional data
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type.value,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "read": self.read,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
