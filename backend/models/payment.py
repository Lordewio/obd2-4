from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from .job import Job

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"

class PaymentMethod(str, Enum):
    CARD = "CARD"
    WALLET = "WALLET"
    BANK_TRANSFER = "BANK_TRANSFER"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    transaction_id = Column(String, nullable=True)
    payment_provider = Column(String, nullable=True)
    payment_details = Column(String, nullable=True)  # JSON string for additional details
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    job = relationship("Job", back_populates="payment")
    user = relationship("User", back_populates="payments")

    def to_dict(self):
        return {
            "id": self.id,
            "job_id": self.job_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "status": self.status.value,
            "method": self.method.value,
            "transaction_id": self.transaction_id,
            "payment_provider": self.payment_provider,
            "payment_details": self.payment_details,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
