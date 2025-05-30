from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

class Diagnostic(Base):
    __tablename__ = 'diagnostics'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    rpm = Column(Integer)
    speed = Column(Float)
    engine_load = Column(Float)
    coolant_temp = Column(Float)
    intake_temp = Column(Float)
    throttle_pos = Column(Float)
    fuel_level = Column(Float)
    has_mil = Column(Boolean)
    dtc_code = Column(String(20))
    dtc_description = Column(String(200))
    severity = Column(Integer)  # 1-5 scale
    latitude = Column(Float)
    longitude = Column(Float)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="diagnostics")

    def __repr__(self):
        return f"<Diagnostic {self.timestamp} - Vehicle {self.vehicle_id}>"
