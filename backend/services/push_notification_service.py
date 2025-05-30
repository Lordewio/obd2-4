import json
from typing import Optional
from firebase_admin import messaging
from firebase_admin import credentials
from firebase_admin import initialize_app
from ..config import settings

# Initialize Firebase Admin SDK
cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT)
initialize_app(cred)

class PushNotificationService:
    @staticmethod
    def send_push_notification(user_id: str, title: str, message: str, data: Optional[str] = None):
        """Send push notification to a user"""
        try:
            # Get device token from user
            device_token = get_device_token(user_id)
            if not device_token:
                return

            # Create notification message
            notification = messaging.Notification(
                title=title,
                body=message
            )

            # Create data payload
            data_payload = {
                "click_action": "FLUTTER_NOTIFICATION_CLICK",
                "type": "notification",
                "title": title,
                "message": message
            }
            if data:
                data_payload["data"] = data

            # Create message
            message = messaging.Message(
                notification=notification,
                data=data_payload,
                token=device_token
            )

            # Send message
            response = messaging.send(message)
            print(f"Successfully sent message: {response}")

        except Exception as e:
            print(f"Error sending push notification: {str(e)}")

    @staticmethod
    def send_job_request_notification(user_id: str, job_id: str, mechanic_name: str):
        """Send job request notification"""
        title = "New Job Request"
        message = f"You have a new job request from {mechanic_name}"
        data = json.dumps({"job_id": job_id, "type": "JOB_REQUEST"})
        PushNotificationService.send_push_notification(user_id, title, message, data)

    @staticmethod
    def send_job_accepted_notification(user_id: str, job_id: str, mechanic_name: str):
        """Send job accepted notification"""
        title = "Job Accepted"
        message = f"Your job request has been accepted by {mechanic_name}"
        data = json.dumps({"job_id": job_id, "type": "JOB_ACCEPTED"})
        PushNotificationService.send_push_notification(user_id, title, message, data)

    @staticmethod
    def send_job_completed_notification(user_id: str, job_id: str, mechanic_name: str):
        """Send job completed notification"""
        title = "Job Completed"
        message = f"Your job has been completed by {mechanic_name}"
        data = json.dumps({"job_id": job_id, "type": "JOB_COMPLETED"})
        PushNotificationService.send_push_notification(user_id, title, message, data)

    @staticmethod
    def send_job_cancelled_notification(user_id: str, job_id: str, mechanic_name: str):
        """Send job cancelled notification"""
        title = "Job Cancelled"
        message = f"Your job request with {mechanic_name} has been cancelled"
        data = json.dumps({"job_id": job_id, "type": "JOB_CANCELLED"})
        PushNotificationService.send_push_notification(user_id, title, message, data)

    @staticmethod
    def send_new_review_notification(user_id: str, job_id: str, user_name: str):
        """Send new review notification"""
        title = "New Review"
        message = f"You have a new review from {user_name}"
        data = json.dumps({"job_id": job_id, "type": "NEW_REVIEW"})
        PushNotificationService.send_push_notification(user_id, title, message, data)

# Helper function to get device token
# This should be implemented based on your device token storage mechanism
def get_device_token(user_id: str) -> Optional[str]:
    """Get device token for a user"""
    # TODO: Implement this based on your device token storage
    return "device_token_here"  # Replace with actual implementation
