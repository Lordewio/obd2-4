from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from ..services.dashboard_service import DashboardService
from ..database import get_db
from ..models import MechanicDashboard, Job, Review

router = APIRouter()

@router.get("/")
async def get_dashboard(mechanic_id: str, db: Session = Depends(get_db)):
    """Get mechanic's dashboard"""
    service = DashboardService(db)
    return service.get_dashboard(mechanic_id)

@router.put("/availability")
async def update_availability(
    mechanic_id: str,
    is_available: bool,
    message: str = None,
    db: Session = Depends(get_db)
):
    """Update mechanic's availability status"""
    service = DashboardService(db)
    return service.update_availability(mechanic_id, is_available, message)

@router.put("/location")
async def update_location(
    mechanic_id: str,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db)
):
    """Update mechanic's current location"""
    service = DashboardService(db)
    return service.update_location(mechanic_id, latitude, longitude)

@router.put("/preferences")
async def update_preferences(
    mechanic_id: str,
    preferences: dict,
    db: Session = Depends(get_db)
):
    """Update mechanic's preferences"""
    service = DashboardService(db)
    return service.update_preferences(mechanic_id, preferences)

@router.get("/active-jobs")
async def get_active_jobs(mechanic_id: str, db: Session = Depends(get_db)):
    """Get mechanic's active jobs"""
    service = DashboardService(db)
    return service.get_active_jobs(mechanic_id)

@router.get("/job-history")
async def get_job_history(mechanic_id: str, db: Session = Depends(get_db)):
    """Get mechanic's job history"""
    service = DashboardService(db)
    return service.get_job_history(mechanic_id)

@router.get("/reviews")
async def get_reviews(mechanic_id: str, db: Session = Depends(get_db)):
    """Get mechanic's reviews"""
    service = DashboardService(db)
    return service.get_reviews(mechanic_id)

@router.get("/statistics")
async def get_statistics(mechanic_id: str, db: Session = Depends(get_db)):
    """Get mechanic's statistics"""
    service = DashboardService(db)
    return service.calculate_statistics(mechanic_id)
