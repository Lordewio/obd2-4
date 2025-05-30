from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class FaultSolution(Base):
    __tablename__ = 'fault_solutions'

    id = Column(Integer, primary_key=True)
    dtc_code = Column(String(10), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    steps_to_fix = Column(Text, nullable=False)
    estimated_cost = Column(Float, nullable=True)
    tools_required = Column(Text, nullable=True)
    difficulty_level = Column(Integer, nullable=False)  # 1-5 scale
    time_to_fix = Column(Integer, nullable=True)  # in minutes
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    vehicle_make = Column(String(50), nullable=True)
    vehicle_model = Column(String(50), nullable=True)
    vehicle_year = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='fault_solutions')
    comments = relationship('FaultSolutionComment', back_populates='solution', cascade='all, delete-orphan')


class FaultSolutionComment(Base):
    __tablename__ = 'fault_solution_comments'

    id = Column(Integer, primary_key=True)
    solution_id = Column(Integer, ForeignKey('fault_solutions.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    comment = Column(Text, nullable=False)
    upvotes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    solution = relationship('FaultSolution', back_populates='comments')
    user = relationship('User')
