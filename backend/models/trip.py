from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from base import Base

class Trip(Base):
    __tablename__ = 'trips'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    start_location = Column(String(100))  # JSON string for coordinates
    end_location = Column(String(100))    # JSON string for coordinates
    distance = Column(Float)  # in kilometers
    average_speed = Column(Float)  # in km/h
    fuel_consumption = Column(Float)  # in liters
    driving_score = Column(Float)  # 0-100 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="trips")

    def __repr__(self):
        return f"<Trip {self.id} - {self.vehicle.make} {self.vehicle.model} ({self.start_time})>"
