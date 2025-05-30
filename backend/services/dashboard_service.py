from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..models import MechanicDashboard, Job, Review
from ..database import get_db
from ..models.user import User
from ..models.job import JobStatus

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_dashboard(self, mechanic_id: str) -> MechanicDashboard:
        """Get mechanic's dashboard"""
        dashboard = self.db.query(MechanicDashboard).filter(
            MechanicDashboard.mechanic_id == mechanic_id
        ).first()
        
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")
            
        return dashboard

    def update_availability(self, mechanic_id: str, is_available: bool, message: str = None) -> MechanicDashboard:
        """Update mechanic's availability status"""
        dashboard = self.get_dashboard(mechanic_id)
        dashboard.is_available = is_available
        dashboard.availability_message = message
        dashboard.last_seen = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(dashboard)
        return dashboard

    def update_location(self, mechanic_id: str, latitude: float, longitude: float) -> MechanicDashboard:
        """Update mechanic's current location"""
        dashboard = self.get_dashboard(mechanic_id)
        dashboard.current_latitude = latitude
        dashboard.current_longitude = longitude
        dashboard.last_seen = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(dashboard)
        return dashboard

    def update_preferences(self, mechanic_id: str, preferences: dict) -> MechanicDashboard:
        """Update mechanic's preferences"""
        dashboard = self.get_dashboard(mechanic_id)
        
        for key, value in preferences.items():
            if hasattr(dashboard, key):
                setattr(dashboard, key, value)
        
        self.db.commit()
        self.db.refresh(dashboard)
        return dashboard

    def get_active_jobs(self, mechanic_id: str) -> list[Job]:
        """Get mechanic's active jobs"""
        return self.db.query(Job).filter(
            Job.mechanic_id == mechanic_id,
            Job.status.in_([JobStatus.ACCEPTED, JobStatus.IN_PROGRESS])
        ).all()

    def get_job_history(self, mechanic_id: str) -> list[Job]:
        """Get mechanic's job history"""
        return self.db.query(Job).filter(
            Job.mechanic_id == mechanic_id,
            Job.status.in_([JobStatus.COMPLETED, JobStatus.CANCELLED])
        ).order_by(Job.created_at.desc()).all()

    def get_reviews(self, mechanic_id: str) -> list[Review]:
        """Get mechanic's reviews"""
        mechanic = self.db.query(User).filter(User.id == mechanic_id).first()
        if not mechanic:
            raise HTTPException(status_code=404, detail="Mechanic not found")
            
        return mechanic.reviews

    def calculate_statistics(self, mechanic_id: str) -> dict:
        """Calculate mechanic's statistics"""
        dashboard = self.get_dashboard(mechanic_id)
        
        total_jobs = self.db.query(Job).filter(Job.mechanic_id == mechanic_id).count()
        completed_jobs = self.db.query(Job).filter(
            Job.mechanic_id == mechanic_id,
            Job.status == JobStatus.COMPLETED
        ).count()
        cancelled_jobs = self.db.query(Job).filter(
            Job.mechanic_id == mechanic_id,
            Job.status == JobStatus.CANCELLED
        ).count()
        
        reviews = self.get_reviews(mechanic_id)
        total_reviews = len(reviews)
        average_rating = sum(review.rating for review in reviews) / total_reviews if total_reviews > 0 else 0.0
        
        return {
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "cancelled_jobs": cancelled_jobs,
            "total_reviews": total_reviews,
            "average_rating": round(average_rating, 1)
        }
