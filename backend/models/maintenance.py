from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import Base

# Define maintenance status enum
class MaintenanceStatus(str, Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class MaintenanceRecord(Base):
    __tablename__ = 'maintenance_records'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    mechanic_id = Column(Integer, ForeignKey('mechanics.id'), nullable=False)
    service_type = Column(String(50), nullable=False)
    description = Column(String(500), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    cost = Column(Float, nullable=False)
    status = Column(Enum(MaintenanceStatus), default=MaintenanceStatus.PENDING)
    next_service_due = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")
    mechanic = relationship("Mechanic", back_populates="maintenance_records")

    def __repr__(self):
        return f"<MaintenanceRecord {self.id} - Vehicle {self.vehicle_id} - Status {self.status}>"
