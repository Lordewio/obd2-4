from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..services.notification_service import NotificationService
from ..database import get_db
from ..models import Notification
from ..models.notification import NotificationType
from pydantic import BaseModel

router = APIRouter()

class NotificationCreate(BaseModel):
    user_id: str
    type: NotificationType
    title: str
    message: str
    data: Optional[str] = None

class NotificationUpdate(BaseModel):
    read: bool

@router.post("/")
async def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db)
):
    """Create a new notification"""
    service = NotificationService(db)
    return service.create_notification(
        notification_data.user_id,
        notification_data.type,
        notification_data.title,
        notification_data.message,
        notification_data.data
    )

@router.get("/user/{user_id}")
async def get_notifications(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get notifications for a user"""
    service = NotificationService(db)
    return service.get_notifications(user_id, limit, offset)

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    service = NotificationService(db)
    return service.mark_notification_as_read(notification_id)

@router.put("/user/{user_id}/read-all")
async def mark_all_as_read(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Mark all notifications for a user as read"""
    service = NotificationService(db)
    return service.mark_all_as_read(user_id)
