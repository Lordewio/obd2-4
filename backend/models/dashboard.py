from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base
from .job import Job
from .user import User

class MechanicDashboard(Base):
    __tablename__ = "mechanic_dashboards"

    id = Column(Integer, primary_key=True, index=True)
    mechanic_id = Column(String, ForeignKey("users.id"), unique=True)
    mechanic = relationship("User", back_populates="dashboard")
    
    # Availability
    is_available = Column(Boolean, default=True)
    availability_message = Column(String, nullable=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    # Statistics
    total_jobs = Column(Integer, default=0)
    completed_jobs = Column(Integer, default=0)
    cancelled_jobs = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    # Location
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    
    # Preferences
    preferred_radius = Column(Float, default=10.0)  # in kilometers
    specialities = Column(String, nullable=True)  # comma-separated list
    
    # Notifications
    notify_new_jobs = Column(Boolean, default=True)
    notify_reviews = Column(Boolean, default=True)
    
    # Relationships
    active_jobs = relationship("Job", back_populates="mechanic_dashboard", foreign_keys=[Job.mechanic_id])
