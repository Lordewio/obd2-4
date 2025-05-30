from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from ..models import Payment, Job, User
from ..database import get_db
from ..models.payment import PaymentStatus, PaymentMethod
from ..services import notification_service, push_notification_service
import stripe
import json

# Initialize Stripe
stripe.api_key = "your_stripe_secret_key"  # Replace with actual Stripe secret key

class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def create_payment_intent(self, job_id: int, amount: float, user_id: str) -> dict:
        """Create a Stripe payment intent"""
        try:
            # Get job details
            job = self.db.query(Job).filter(Job.id == job_id).first()
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")

            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency="usd",
                payment_method_types=["card"],
                metadata={
                    "job_id": str(job_id),
                    "user_id": user_id
                }
            )

            # Create payment record
            payment = Payment(
                job_id=job_id,
                user_id=user_id,
                amount=amount,
                status=PaymentStatus.PENDING,
                method=PaymentMethod.CARD,
                transaction_id=payment_intent.id,
                payment_provider="stripe",
                payment_details=json.dumps(payment_intent)
            )
            
            self.db.add(payment)
            self.db.commit()
            self.db.refresh(payment)

            return {
                "client_secret": payment_intent.client_secret,
                "payment_id": payment.id
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def process_payment_webhook(self, payload: dict) -> None:
        """Process Stripe webhook events"""
        try:
            # Verify and parse webhook event
            event = stripe.Event.construct_from(
                payload, stripe.api_key
            )

            # Handle different event types
            if event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                payment_id = payment_intent.metadata.get('payment_id')
                
                if payment_id:
                    payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
                    if payment:
                        payment.status = PaymentStatus.COMPLETED
                        payment.transaction_id = payment_intent.id
                        payment.payment_details = json.dumps(payment_intent)
                        self.db.commit()

                        # Send notification
                        notification_service.create_notification(
                            user_id=payment.user_id,
                            notification_type="PAYMENT_RECEIVED",
                            title="Payment Received",
                            message=f"Payment of ${payment.amount:.2f} has been successfully received for job #{payment.job_id}",
                            data=json.dumps({"payment_id": payment.id, "job_id": payment.job_id})
                        )

                        # Update job status
                        job = payment.job
                        job.status = "COMPLETED"
                        self.db.commit()

            elif event.type == 'payment_intent.payment_failed':
                payment_intent = event.data.object
                payment_id = payment_intent.metadata.get('payment_id')
                
                if payment_id:
                    payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
                    if payment:
                        payment.status = PaymentStatus.FAILED
                        payment.payment_details = json.dumps(payment_intent)
                        self.db.commit()

                        # Send notification
                        notification_service.create_notification(
                            user_id=payment.user_id,
                            notification_type="PAYMENT_FAILED",
                            title="Payment Failed",
                            message=f"Payment for job #{payment.job_id} failed. Please try again.",
                            data=json.dumps({"payment_id": payment.id, "job_id": payment.job_id})
                        )

        except Exception as e:
            print(f"Error processing webhook: {str(e)}")

    def get_payment(self, payment_id: int) -> Payment:
        """Get payment details"""
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def get_payments_for_user(self, user_id: str, limit: int = 50, offset: int = 0) -> list:
        """Get user's payment history"""
        return self.db.query(Payment).filter(
            Payment.user_id == user_id
        ).order_by(Payment.created_at.desc()).limit(limit).offset(offset).all()

    def refund_payment(self, payment_id: int) -> dict:
        """Refund a payment"""
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")

        if payment.status != PaymentStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Payment not completed")

        try:
            # Create refund
            refund = stripe.Refund.create(
                payment_intent=payment.transaction_id
            )

            # Update payment status
            payment.status = PaymentStatus.REFUNDED
            payment.payment_details = json.dumps(refund)
            self.db.commit()

            # Send notification
            notification_service.create_notification(
                user_id=payment.user_id,
                notification_type="PAYMENT_REFUNDED",
                title="Payment Refunded",
                message=f"Payment of ${payment.amount:.2f} has been refunded for job #{payment.job_id}",
                data=json.dumps({"payment_id": payment.id, "job_id": payment.job_id})
            )

            return refund

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
