from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..services.review_service import ReviewService
from ..database import get_db
from ..models import Review, Job, JobStatus
from pydantic import BaseModel

router = APIRouter()

class ReviewCreate(BaseModel):
    user_id: str
    mechanic_id: str
    job_id: int
    rating: float
    comment: str

class ReviewUpdate(BaseModel):
    rating: Optional[float] = None
    comment: Optional[str] = None

class ReviewStats(BaseModel):
    total_reviews: int
    average_rating: float
    rating_distribution: dict

@router.post("/")
async def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db)
):
    """Create a new review"""
    service = ReviewService(db)
    return service.create_review(
        review_data.user_id,
        review_data.mechanic_id,
        review_data.job_id,
        review_data.rating,
        review_data.comment
    )

@router.get("/mechanic/{mechanic_id}")
async def get_reviews_for_mechanic(
    mechanic_id: str,
    db: Session = Depends(get_db)
):
    """Get all reviews for a mechanic"""
    service = ReviewService(db)
    return service.get_reviews_for_mechanic(mechanic_id)

@router.get("/mechanic/{mechanic_id}/stats")
async def get_review_stats(
    mechanic_id: str,
    db: Session = Depends(get_db)
):
    """Get review statistics for a mechanic"""
    service = ReviewService(db)
    return service.get_review_stats(mechanic_id)

@router.put("/{review_id}")
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db)
):
    """Update a review"""
    service = ReviewService(db)
    return service.update_review(review_id, review_data.rating, review_data.comment)

@router.put("/{review_id}/status")
async def update_review_status(
    review_id: int,
    status: JobStatus,
    db: Session = Depends(get_db)
):
    """Update review status"""
    service = ReviewService(db)
    return service.update_review_status(review_id, status)
