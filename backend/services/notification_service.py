from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models import Notification, User
from ..database import get_db
from ..models.notification import NotificationType
from ..services import push_notification_service

class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(self, user_id: str, notification_type: NotificationType, title: str, message: str, data: Optional[str] = None) -> Notification:
        """Create a new notification"""
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create notification
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            data=data
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        # Send push notification
        push_notification_service.send_push_notification(user_id, title, message, data)
        
        return notification

    def get_notifications(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Notification]:
        """Get notifications for a user"""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).limit(limit).offset(offset).all()

    def mark_notification_as_read(self, notification_id: int) -> Notification:
        """Mark a notification as read"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        notification.read = True
        notification.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(notification)
        
        return notification

    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications for a user as read"""
        notifications = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.read == False
        ).all()
        
        for notification in notifications:
            notification.read = True
            notification.updated_at = datetime.utcnow()
        
        self.db.commit()
        return len(notifications)
