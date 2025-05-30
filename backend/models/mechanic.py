from sqlalchemy import Column, Integer, String, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import Base

# Define mechanic status enum
class MechanicStatus(str, Enum):
    AVAILABLE = 'available'
    BUSY = 'busy'
    OFFLINE = 'offline'

class Mechanic(Base):
    __tablename__ = 'mechanics'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    speciality = Column(String(100))
    experience_years = Column(Integer)
    rating = Column(Float, default=0.0)
    status = Column(Enum(MechanicStatus), default=MechanicStatus.OFFLINE)
    availability = Column(String(50))  # e.g., "9am-5pm"
    location_latitude = Column(Float)
    location_longitude = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="mechanic")
    maintenance_records = relationship("MaintenanceRecord", back_populates="mechanic")
    reviews = relationship("Review", back_populates="mechanic")

    def __repr__(self):
        return f"<Mechanic {self.id} - Status {self.status} - Rating {self.rating}>"
