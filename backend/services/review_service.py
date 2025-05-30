from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Review, Job, User
from ..database import get_db
from ..models.job import JobStatus
from datetime import datetime

class ReviewService:
    def __init__(self, db: Session):
        self.db = db

    def create_review(self, user_id: str, mechanic_id: str, job_id: int, rating: float, comment: str) -> Review:
        """Create a new review"""
        # Check if job exists and is completed
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status != JobStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Job must be completed to leave a review")

        # Check if review already exists
        existing_review = self.db.query(Review).filter(
            Review.job_id == job_id,
            Review.user_id == user_id
        ).first()
        if existing_review:
            raise HTTPException(status_code=400, detail="Review already exists for this job")

        # Create review
        review = Review(
            user_id=user_id,
            mechanic_id=mechanic_id,
            job_id=job_id,
            rating=rating,
            comment=comment,
            status=JobStatus.PENDING
        )
        
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        
        return review

    def get_reviews_for_mechanic(self, mechanic_id: str) -> List[Review]:
        """Get all reviews for a mechanic"""
        return self.db.query(Review).filter(
            Review.mechanic_id == mechanic_id,
            Review.status == JobStatus.COMPLETED
        ).order_by(Review.created_at.desc()).all()

    def get_review_stats(self, mechanic_id: str) -> dict:
        """Get review statistics for a mechanic"""
        reviews = self.get_reviews_for_mechanic(mechanic_id)
        
        total_reviews = len(reviews)
        if total_reviews == 0:
            return {
                "total_reviews": 0,
                "average_rating": 0.0,
                "rating_distribution": {
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 0
                }
            }

        total_rating = sum(review.rating for review in reviews)
        average_rating = round(total_rating / total_reviews, 1)
        
        rating_distribution = {
            "1": len([r for r in reviews if r.rating == 1]),
            "2": len([r for r in reviews if r.rating == 2]),
            "3": len([r for r in reviews if r.rating == 3]),
            "4": len([r for r in reviews if r.rating == 4]),
            "5": len([r for r in reviews if r.rating == 5])
        }

        return {
            "total_reviews": total_reviews,
            "average_rating": average_rating,
            "rating_distribution": rating_distribution
        }

    def update_review_status(self, review_id: int, status: JobStatus) -> Review:
        """Update review status"""
        review = self.db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")

        review.status = status
        review.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(review)
        
        return review
