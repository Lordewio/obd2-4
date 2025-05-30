from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from base import Base

class Geofence(Base):
    __tablename__ = 'geofences'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Float)  # in meters
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="geofences")

    def __repr__(self):
        return f"<Geofence {self.name} - Vehicle {self.vehicle_id} ({self.radius}m radius)>"
